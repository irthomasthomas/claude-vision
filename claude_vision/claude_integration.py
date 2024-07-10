import os
import requests
import json
from .config import ANTHROPIC_API_KEY
from .utils import logger

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"

def claude_vision_analysis(base64_images, prompt, output_type, stream=False, system_prompt=None, max_tokens=1000):
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

    data = {
        "model": "claude-3-5-sonnet-20240620",
        "max_tokens": max_tokens,
        "system": system_prompt or system_prompts[output_type],
        "messages": [{"role": "user", "content": content}],
        "stream": stream
    }

    try:
        response = requests.post(ANTHROPIC_API_URL, headers=headers, json=data, stream=stream)
        response.raise_for_status()

        if stream:
            return response.iter_lines()
        else:
            result = response.json()
            return result['content'][0]['text']
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in Claude vision analysis: {str(e)}")
        raise