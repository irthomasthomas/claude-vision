import httpx
import json
from typing import List, Dict, Any, AsyncGenerator, Union, Callable, TypeVar
from functools import wraps
from enum import Enum, IntEnum
from dataclasses import dataclass, asdict
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from .config import ANTHROPIC_API_KEY
from .utils import logger
from .exceptions import (
    InvalidRequestError, AuthenticationError, PermissionError,
    NotFoundError, RateLimitError, APIError, OverloadedError
)
from .image_processing import ProcessedImage

# Constants
ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_API_VERSION = "2023-06-01"
DEFAULT_TIMEOUT = 180.0
DEFAULT_MAX_TOKENS = 1000
MODEL_NAME = "claude-3-5-sonnet-20240620"
DEFAULT_SYSTEM_PROMPT = "You are Claude 3.5 Sonnet, an AI assistant with vision capabilities. Describe the image."

class OutputType(Enum):
    TEXT = "text"
    JSON = "json"
    MD = "md"

class HttpStatusCode(IntEnum):
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    TOO_MANY_REQUESTS = 429
    INTERNAL_SERVER_ERROR = 500
    SERVICE_OVERLOADED = 529

class ImageMediaType(Enum):
    PNG = "image/png"
    JPEG = "image/jpeg"
    GIF = "image/gif"

@dataclass
class RequestData:
    model: str
    max_tokens: int
    system: str
    messages: List[Dict[str, Any]]
    stream: bool
    
def handle_api_errors(func: Callable):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            logger.error(f"Response content: {e.response.text}")
            handle_http_error(e)
        except httpx.RequestError as e:
            logger.error(f"Request error occurred: {e}")
            raise APIError(f"Request error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            raise APIError(f"Invalid JSON response from API: {str(e)}")
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}", exc_info=True)
            raise APIError(f"An unexpected error occurred: {str(e)}")
    return wrapper


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry=retry_if_exception_type((httpx.RequestError, httpx.HTTPStatusError))
)
@handle_api_errors
@dataclass
class ProcessedImage:
    base64: str
    estimated_tokens: int


@handle_api_errors
async def claude_vision_analysis(
    base64_images: List[str],
    prompt: str,
    output_type: str,
    stream: bool = False,
    system: str = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    prefill: str = None,
) -> AsyncGenerator[str, None]:
    """
    Perform Claude Vision analysis on the provided processed images.

    Args:
        processed_images (List[ProcessedImage]): List of ProcessedImage objects.
        prompt (str): The prompt for the analysis.
        output_type (OutputType): The desired output type.
        stream (bool, optional): Whether to stream the response. Defaults to False.
        system (str, optional): Custom system prompt. Defaults to None.
        max_tokens (int, optional): Maximum number of tokens in the response. Defaults to DEFAULT_MAX_TOKENS.
        prefill (str, optional): Prefill text for the response. Defaults to None.

    Returns:
        AsyncGenerator[str, None]: The analysis result as an async generator.
    """
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION,
        "Accept": "application/json"
    }
    base64_images = [img.base64 for img in processed_images]
    
    data = create_request_data(base64_images, prompt, output_type, stream, system, max_tokens, prefill)

    async with httpx.AsyncClient() as client:
        response = await send_request(client, headers, data)
        async for chunk in handle_response(response, stream, output_type):
            yield chunk
    
    
def create_request_data(base64_images: List[str], prompt: str, output_type: OutputType, 
                        stream: bool, system: str, max_tokens: int, prefill: str) -> RequestData:
    """
    Create the request data for the API call.

    Args:
        base64_images (List[str]): List of base64-encoded images.
        prompt (str): The prompt for the analysis.
        output_type (OutputType): The desired output type.
        stream (bool): Whether to stream the response.
        system (str): Custom system prompt.
        max_tokens (int): Maximum number of tokens in the response.
        prefill (str): Prefill text for the response.

    Returns:
        RequestData: The structured request data.
    """
    content = [{"type": "text", "text": prompt}]
    content.extend([{
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": ImageMediaType.PNG.value,
            "data": img
        }
    } for img in base64_images])

    messages = [{"role": "user", "content": content}]
    if output_type == OutputType.JSON and not prefill:
        prefill = '{'
    if prefill:
        messages.append({"role": "assistant", "content": prefill.rstrip()})

    return RequestData(
        model=MODEL_NAME,
        max_tokens=max_tokens,
        system=system or get_system_prompt(output_type),
        messages=messages,
        stream=stream
    )
        
def get_system_prompt(output_type: OutputType) -> str:
    systems = {
        OutputType.TEXT: DEFAULT_SYSTEM_PROMPT,
        OutputType.JSON: "Analyze the image and provide output in valid JSON format only. No additional text.",
        OutputType.MD: "Analyze the image and provide output in valid Markdown format only. No additional text."
    }
    return systems.get(output_type, DEFAULT_SYSTEM_PROMPT)


def estimate_image_tokens(base64_image: str) -> int:
    """
    Estimate the number of tokens for a base64 encoded image.
    This is a rough estimate and may not be exact.
    """
    return len(base64_image) // 3  # Rough estimate: 1 token per 3 base64 characters


async def send_request(client: httpx.AsyncClient, headers: Dict[str, str], data: RequestData) -> httpx.Response:
    logger.debug(f"Sending request to Anthropic API: {ANTHROPIC_API_URL}")
    response = await client.post(ANTHROPIC_API_URL, headers=headers, json=asdict(data), timeout=DEFAULT_TIMEOUT)
    logger.debug(f"Received response from Anthropic API. Status code: {response.status_code}")
    response.raise_for_status()
    return response

async def handle_response(response: httpx.Response, stream: bool, output_type: OutputType) -> AsyncGenerator[str, None]:
    if stream:
        async for chunk in handle_stream_response(response):
            yield chunk
    else:
        yield handle_non_stream_response(response, output_type)

async def handle_stream_response(response: httpx.Response) -> AsyncGenerator[str, None]:
    async for line in response.aiter_lines():
        if line.startswith('data: '):
            event = json.loads(line[6:])
            if event['type'] == 'content_block_delta':
                yield event['delta'].get('text', '')
            elif event['type'] == 'message_stop':
                break

def handle_non_stream_response(response: httpx.Response, output_type: OutputType) -> str:
    result = response.json()
    content = result['content'][0]['text']
    if output_type == OutputType.JSON:
        content = '{' + content.lstrip('{')  # Ensure it starts with '{'
    return content

def handle_http_error(e: httpx.HTTPStatusError) -> None:
    error_map = {
        HttpStatusCode.BAD_REQUEST: InvalidRequestError,
        HttpStatusCode.UNAUTHORIZED: AuthenticationError,
        HttpStatusCode.FORBIDDEN: PermissionError,
        HttpStatusCode.NOT_FOUND: NotFoundError,
        HttpStatusCode.TOO_MANY_REQUESTS: RateLimitError,
        HttpStatusCode.INTERNAL_SERVER_ERROR: APIError,
        HttpStatusCode.SERVICE_OVERLOADED: OverloadedError
    }
    error_class = error_map.get(HttpStatusCode(e.response.status_code), APIError)
    error_message = e.response.json().get('error', {}).get('message', str(e))
    raise error_class(f"API error ({e.response.status_code}): {error_message}")