import io
import base64
from PIL import Image
import httpx
import asyncio
from typing import List, Union
from .config import MAX_IMAGE_SIZE, SUPPORTED_FORMATS
from .utils import logger
from .exceptions import InvalidRequestError
import numpy as np
import cv2

async def fetch_image_from_url(url: str, client: httpx.AsyncClient) -> Image.Image:
    try:
        response = await client.get(url)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching image from URL {url}: {str(e)}")
        raise InvalidRequestError(f"Failed to fetch image from URL: {url}")

def convert_image_to_base64(image: Image.Image) -> str:
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def check_and_resize_image(image: Image.Image, max_size: tuple = MAX_IMAGE_SIZE) -> Image.Image:
    if image.width > max_size[0] or image.height > max_size[1]:
        image.thumbnail(max_size, Image.LANCZOS)
    return image

def estimate_image_tokens(image: Image.Image) -> int:
    return (image.width * image.height) // 750

def open_image(image_path: str) -> Image.Image:
    try:
        with Image.open(image_path) as img:
            return img.copy()
    except Exception as e:
        logger.error(f"Error opening image {image_path}: {str(e)}")
        raise InvalidRequestError(f"Failed to open image: {image_path}")

async def process_image_source(source: Union[str, Image.Image, io.BytesIO, np.ndarray], client: httpx.AsyncClient) -> str:
    try:
        if isinstance(source, str):
            if source.startswith(('http://', 'https://')):
                image = await fetch_image_from_url(source, client)
            else:
                image = open_image(source)
        elif isinstance(source, Image.Image):
            image = source
        elif isinstance(source, io.BytesIO):
            image = Image.open(source)
        elif isinstance(source, np.ndarray):
            image = Image.fromarray(cv2.cvtColor(source, cv2.COLOR_BGR2RGB))
        else:
            raise InvalidRequestError(f"Unsupported image source type: {type(source)}")
        
        if image.format not in SUPPORTED_FORMATS:
            image = image.convert('RGB')

        image = check_and_resize_image(image)
        estimated_tokens = estimate_image_tokens(image)
        logger.info(f"Estimated tokens for image: {estimated_tokens}")
        
        return convert_image_to_base64(image)
    except Exception as e:
        logger.error(f"Error processing image source: {str(e)}")
        raise InvalidRequestError(f"Failed to process image: {str(e)}")    
    
    
async def process_multiple_images(image_sources: List[Union[str, Image.Image, io.BytesIO]], process_as_group: bool = False) -> List[str]:
    MAX_IMAGES = 20

    if len(image_sources) > MAX_IMAGES:
        raise InvalidRequestError(f"Too many images. Maximum allowed is {MAX_IMAGES}, but {len(image_sources)} were provided.")

    async with httpx.AsyncClient() as client:
        tasks = [process_image_source(source, client) for source in image_sources[:MAX_IMAGES]]
        return await asyncio.gather(*tasks)
