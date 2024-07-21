
import httpx
import json
from typing import List, Dict, Any, AsyncGenerator, Union
from .config import ANTHROPIC_API_KEY
from .utils import logger
from .exceptions import (
    InvalidRequestError, AuthenticationError, PermissionError,
    NotFoundError, RateLimitError, APIError, OverloadedError
)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

async def claude_vision_analysis(
    base64_images: List[str],
    prompt: str,
    output_type: str,
    stream: bool = False,
    system_prompt: str = None,
    max_tokens: int = 1000,
    prefill: str = None,
    tools: List[Dict[str, Any]] = None
) -> Union[str, AsyncGenerator[str, None]]:
    headers = {
        "Content-Type": "application/json",
        "x-api-key": ANTHROPIC_API_KEY,
        "anthropic-version": "2023-06-01"
    }

    system_prompts = {
        'text': "You are Claude 3.5 Sonnet, an AI assistant with vision capabilities. Describe the image.",
        'json': "Analyze the image and provide output in valid JSON format only. No additional text.",
        'md': "Analyze the image and provide output in valid Markdown format only. No additional text."
    }

    content = [{"type": "text", "text": prompt}]
    for base64_image in base64_images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": "image/png",
                "data": base64_image
            }
        })

    messages = [{"role": "user", "content": content}]
    if output_type == 'json' and not prefill:
        prefill = '{'
    if prefill:
        messages.append({"role": "assistant", "content": prefill})

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": max_tokens,
        "system": system_prompt or system_prompts.get(output_type, system_prompts['text']),
        "messages": messages,
        "stream": stream
    }

    if tools:
        data["tools"] = tools

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(ANTHROPIC_API_URL, headers=headers, json=data, timeout=180.0)
            response.raise_for_status()

            if stream:
                return handle_stream_response(response)
            else:
                result = response.json()
                content = result['content'][0]['text']
                if output_type == 'json':
                    content = '{' + content.lstrip('{')  # Ensure it starts with '{'
                return content
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error occurred: {e}")
            handle_http_error(e)
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            raise APIError(f"An unexpected error occurred: {str(e)}")

async def handle_stream_response(response: httpx.Response) -> AsyncGenerator[str, None]:
    async for line in response.aiter_lines():
        if line.startswith('data: '):
            event = json.loads(line[6:])
            if event['type'] == 'content_block_delta':
                yield event['delta'].get('text', '')
            elif event['type'] == 'message_stop':
                break

def handle_http_error(e: httpx.HTTPStatusError):
    error_map = {
        400: InvalidRequestError,
        401: AuthenticationError,
        403: PermissionError,
        404: NotFoundError,
        429: RateLimitError,
        500: APIError,
        529: OverloadedError
    }
    error_class = error_map.get(e.response.status_code, APIError)
    error_message = e.response.json().get('error', {}).get('message', str(e))
    raise error_class(error_message)