import httpx
import json
from typing import List, Dict, Any, AsyncGenerator, Union, Callable
from functools import wraps
from enum import Enum, IntEnum
from dataclasses import dataclass, asdict
from .config import ANTHROPIC_API_KEY
from .utils import logger
from .exceptions import (
    InvalidRequestError, AuthenticationError, PermissionError,
    NotFoundError, RateLimitError, APIError, OverloadedError
)

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

@handle_api_errors
async def claude_vision_analysis(
    base64_images: List[str],
    prompt: str,
    output_type: OutputType,
    stream: bool = False,
    system: str = None,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    prefill: str = None,
) -> Union[str, AsyncGenerator[str, None]]:
    headers = create_headers()
    data = create_request_data(base64_images, prompt, output_type, stream, system, max_tokens, prefill)

    async with httpx.AsyncClient() as client:
        response = await send_request(client, headers, data)
        return await handle_response(response, stream, output_type)

def create_headers() -> Dict[str, str]:
    return {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": ANTHROPIC_API_VERSION
    }

def create_request_data(base64_images: List[str], prompt: str, output_type: OutputType, 
                        stream: bool, system: str, max_tokens: int, prefill: str) -> RequestData:
    content = [{"type": "text", "text": prompt}]
    content.extend([{
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": "image/png",
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
    return systems[output_type]

async def send_request(client: httpx.AsyncClient, headers: Dict[str, str], data: RequestData) -> httpx.Response:
    logger.debug(f"Sending request to Anthropic API: {ANTHROPIC_API_URL}")
    response = await client.post(ANTHROPIC_API_URL, headers=headers, json=asdict(data), timeout=DEFAULT_TIMEOUT)
    logger.debug(f"Received response from Anthropic API. Status code: {response.status_code}")
    response.raise_for_status()
    return response

async def handle_response(response: httpx.Response, stream: bool, output_type: OutputType) -> Union[str, AsyncGenerator[str, None]]:
    if stream:
        return handle_stream_response(response)
    else:
        return handle_non_stream_response(response, output_type)

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