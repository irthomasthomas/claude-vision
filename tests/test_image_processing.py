
import pytest
import os
import io
from PIL import Image
from claude_vision.image_processing import (
    convert_image_to_base64,
    check_and_resize_image,
    estimate_image_tokens,
    process_image_source,
    process_multiple_images
)
from claude_vision.exceptions import InvalidRequestError

TEST_IMAGE_DIR = '/home/ShellLM/Projects/claude-vision/tests'

@pytest.fixture
def sample_image():
    return Image.open(os.path.join(TEST_IMAGE_DIR, 'sample.jpg'))

def test_convert_image_to_base64(sample_image):
    base64_string = convert_image_to_base64(sample_image)
    assert isinstance(base64_string, str)
    assert base64_string.startswith('iVBORw0KGgo')

def test_check_and_resize_image(sample_image):
    resized_image = check_and_resize_image(sample_image, (100, 100))
    assert resized_image.width <= 100
    assert resized_image.height <= 100

def test_estimate_image_tokens(sample_image):
    tokens = estimate_image_tokens(sample_image)
    assert isinstance(tokens, int)
    assert tokens > 0

@pytest.mark.asyncio
async def test_process_image_source():
    image_path = os.path.join(TEST_IMAGE_DIR, 'sample.jpg')
    base64_image = await process_image_source(image_path, None)
    assert isinstance(base64_image, str)
    assert base64_image.startswith('iVBORw0KGgo')

@pytest.mark.asyncio
async def test_process_multiple_images():
    image_paths = [
        os.path.join(TEST_IMAGE_DIR, 'sample.jpg'),
        os.path.join(TEST_IMAGE_DIR, 'sample2.png')
    ]
    base64_images = await process_multiple_images(image_paths)
    assert len(base64_images) == 2
    assert all(isinstance(img, str) for img in base64_images)

@pytest.mark.asyncio
async def test_process_invalid_image():
    with pytest.raises(InvalidRequestError):
        await process_image_source('nonexistent.jpg', None)

@pytest.mark.asyncio
async def test_process_too_many_images():
    image_paths = [os.path.join(TEST_IMAGE_DIR, 'sample.jpg')] * 21
    with pytest.raises(InvalidRequestError):
        await process_multiple_images(image_paths)