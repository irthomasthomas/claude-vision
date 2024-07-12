import io
import base64
from PIL import Image
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from .config import MAX_IMAGE_SIZE, SUPPORTED_FORMATS
from .utils import logger

def fetch_image_from_url(url, max_retries=3):
    retry_strategy = Retry(
        total=max_retries,
        backoff_factor=0.1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        return Image.open(io.BytesIO(response.content))
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching image from URL {url}: {str(e)}")
        raise

def convert_image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

def resize_image(image, max_size=MAX_IMAGE_SIZE):
    image.thumbnail(max_size, Image.LANCZOS)
    return image

def open_image(image_path):
    try:
        with Image.open(image_path) as img:
            in_memory_img = img.copy()
        if in_memory_img is None:
            raise ValueError(f"Failed to open image: {image_path}")
        return in_memory_img
    except Exception as e:
        logger.error(f"Error opening image {image_path}: {str(e)}")
        raise

def process_image(image_source):
    try:
        if isinstance(image_source, str):
            if image_source.startswith(('http://', 'https://')):
                image = fetch_image_from_url(image_source)
            else:
                image = open_image(image_source)
        elif isinstance(image_source, Image.Image):
            image = image_source
        else:
            raise ValueError(f"Unsupported image source type: {type(image_source)}")
        
        # Ensure image is in a supported format
        if image.format not in SUPPORTED_FORMATS:
            image = image.convert('RGB')

        resized_img = resize_image(image)
        base64_image = convert_image_to_base64(resized_img)
        return base64_image
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        raise