import io
import base64
from enum import Enum
from dataclasses import dataclass
from typing import List, Union, Any, Callable, Dict

import numpy as np
import cv2
from PIL import Image
import httpx
import asyncio

from .config import MAX_IMAGE_SIZE, SUPPORTED_FORMATS
from .utils import logger
from .exceptions import InvalidRequestError

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

class ImageProcessor:
    @staticmethod
    async def fetch_image_from_url(url: str, client: httpx.AsyncClient) -> Image.Image:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return Image.open(io.BytesIO(response.content))
        except httpx.HTTPStatusError as e:
            logger.error(f"Error fetching image from URL {url}: {str(e)}")
            raise InvalidRequestError(f"Failed to fetch image from URL: {url}")

    @staticmethod
    def convert_image_to_base64(image: Image.Image) -> str:
        with io.BytesIO() as buffered:
            image.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')

    @staticmethod
    def check_and_resize_image(image: Image.Image, max_size: tuple = MAX_IMAGE_SIZE) -> Image.Image:
        if image.width > max_size[0] or image.height > max_size[1]:
            image.thumbnail(max_size, Image.LANCZOS)
        return image

    @staticmethod
    def estimate_image_tokens(image: Image.Image) -> int:
        return (image.width * image.height) // 750

    @staticmethod
    def open_image(image_path: str) -> Image.Image:
        try:
            return Image.open(image_path).copy()
        except Exception as e:
            logger.error(f"Error opening image {image_path}: {str(e)}")
            raise InvalidRequestError(f"Failed to open image: {image_path}")

    @classmethod
    async def process_image_source(cls, source: Union[str, Image.Image, io.BytesIO, np.ndarray], client: httpx.AsyncClient) -> ProcessedImage:
        try:
            image_type = cls.determine_image_type(source)
            image = await cls.get_image(source, image_type, client)
            
            if image.format not in SUPPORTED_FORMATS:
                image = image.convert('RGB')

            image = cls.check_and_resize_image(image)
            estimated_tokens = cls.estimate_image_tokens(image)
            logger.info(f"Estimated tokens for image: {estimated_tokens}")
            
            return ProcessedImage(
                base64=cls.convert_image_to_base64(image),
                estimated_tokens=estimated_tokens
            )
        except Exception as e:
            logger.error(f"Error processing image source: {str(e)}")
            raise

    @staticmethod
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

    @classmethod
    async def get_image(cls, source: Union[str, Image.Image, io.BytesIO, np.ndarray], image_type: ImageSource, client: httpx.AsyncClient) -> Image.Image:
        image_handlers: Dict[ImageSource, Callable] = {
            ImageSource.URL: lambda: cls.fetch_image_from_url(source, client),
            ImageSource.FILE: lambda: cls.open_image(source),
            ImageSource.PILLOW: lambda: source,
            ImageSource.BYTES: lambda: Image.open(source),
            ImageSource.NUMPY: lambda: Image.fromarray(cv2.cvtColor(source, cv2.COLOR_BGR2RGB))
        }
        return await image_handlers[image_type]()

async def process_multiple_images(image_sources: List[Union[str, Image.Image, io.BytesIO]]) -> List[ProcessedImage]:
    MAX_IMAGES = 20
    
    if len(image_sources) > MAX_IMAGES:
        raise InvalidRequestError(f"Too many images. Maximum allowed is {MAX_IMAGES}, but {len(image_sources)} were provided.")
    
    async with httpx.AsyncClient() as client:
        tasks = [ImageProcessor.process_image_source(source, client) for source in image_sources[:MAX_IMAGES]]
        return await asyncio.gather(*tasks)