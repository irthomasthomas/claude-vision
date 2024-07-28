import io
import base64
from PIL import Image
import httpx
import asyncio
from typing import List, Union
import numpy as np
import cv2
from enum import Enum
from dataclasses import dataclass

from .config import MAX_IMAGE_SIZE, SUPPORTED_FORMATS
from .utils import logger
from .exceptions import InvalidRequestError

import base64
import re


class ImageSource(Enum):
    URL = "url"
    FILE = "file"
    PILLOW = "pillow"
    BYTES = "bytes"
    NUMPY = "numpy"

@dataclass
class ProcessedImage:
    base64: str
    estimated_tokens: int

async def fetch_image_from_url(url: str, client: httpx.AsyncClient) -> Image.Image:
    try:
        response = await client.get(url)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except httpx.HTTPStatusError as e:
        logger.error(f"Error fetching image from URL {url}: {str(e)}")
        raise InvalidRequestError(f"Failed to fetch image from URL: {url}")

def convert_image_to_base64(image: Image.Image) -> str:
    with io.BytesIO() as buffered:
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
        return Image.open(image_path).copy()
    except Exception as e:
        logger.error(f"Error opening image {image_path}: {str(e)}")
        raise InvalidRequestError(f"Failed to open image: {image_path}")

async def process_image_source(source: Union[str, Image.Image, io.BytesIO, np.ndarray], client: httpx.AsyncClient) -> ProcessedImage:
    try:
        image_type = determine_image_type(source)
        image = await get_image(source, image_type, client)
        
        if image.format not in SUPPORTED_FORMATS:
            image = image.convert('RGB')

        image = check_and_resize_image(image)
        estimated_tokens = estimate_image_tokens(image)
        logger.info(f"Estimated tokens for image: {estimated_tokens}")
        
        # Convert image to PNG format
        with io.BytesIO() as buffered:
            image.save(buffered, format="PNG")
            img_byte_arr = buffered.getvalue()
        
        # Encode to base64
        base64_str = base64.b64encode(img_byte_arr).decode('utf-8')
        
        # Validate base64 string
        try:
            decoded = base64.b64decode(base64_str)
            Image.open(io.BytesIO(decoded))
        except Exception as e:
            logger.error(f"Invalid base64 string: {str(e)}")
            raise InvalidRequestError(f"Failed to validate base64 string: {str(e)}")
        
        logger.debug(f"Base64 string length: {len(base64_str)}")
        logger.debug(f"Base64 string preview: {base64_str[:50]}...")
        
        return ProcessedImage(
            base64=base64_str,
            estimated_tokens=estimated_tokens
        )
    except Exception as e:
        logger.error(f"Error processing image source: {str(e)}")
        raise InvalidRequestError(f"Failed to process image: {str(e)}")

def determine_image_type(source: Union[str, Image.Image, io.BytesIO, np.ndarray]) -> ImageSource:
    if isinstance(source, str):
        return ImageSource.URL if source.startswith(('http://', 'https://')) else ImageSource.FILE
    elif isinstance(source, Image.Image):
        return ImageSource.PILLOW
    elif isinstance(source, io.BytesIO):
        return ImageSource.BYTES
    elif isinstance(source, np.ndarray):
        return ImageSource.NUMPY
    else:
        raise InvalidRequestError(f"Unsupported image source type: {type(source)}")

async def get_image(source: Union[str, Image.Image, io.BytesIO, np.ndarray], image_type: ImageSource, client: httpx.AsyncClient) -> Image.Image:
    if image_type == ImageSource.URL:
        return await fetch_image_from_url(source, client)
    elif image_type == ImageSource.FILE:
        return open_image(source)
    elif image_type == ImageSource.PILLOW:
        return source
    elif image_type == ImageSource.BYTES:
        return Image.open(source)
    elif image_type == ImageSource.NUMPY:
        return Image.fromarray(cv2.cvtColor(source, cv2.COLOR_BGR2RGB))

async def process_multiple_images(image_sources: List[Union[str, Image.Image, io.BytesIO, np.ndarray]], process_as_group: bool = False) -> List[ProcessedImage]:
    MAX_IMAGES = 20    
    if len(image_sources) > MAX_IMAGES:
        raise InvalidRequestError(f"Too many images. Maximum allowed is {MAX_IMAGES}, but {len(image_sources)} were provided.")
    
    async with httpx.AsyncClient() as client:
        tasks = [process_image_source(source, client) for source in image_sources[:MAX_IMAGES]]
        return await asyncio.gather(*tasks)