# core.py
from typing import List

# Image processing
from .image_processing import (
    convert_image_to_base64,
    check_and_resize_image,
    estimate_image_tokens,
    process_image_source,
    process_multiple_images
)

# Claude integration
from .claude_integration import claude_vision_analysis

# Exceptions
from .exceptions import (
    ClaudeVisionError,
    InvalidRequestError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    APIError,
    OverloadedError
)

# Configuration
from .config import Configuration

# Advanced features
from .advanced_features import (
    visual_judge,
    image_evolution_analyzer,
    persona_based_analysis,
    comparative_time_series_analysis,
    generate_alt_text
)

# Utilities
from .utils import logger

# Define categories for better organization
IMAGE_PROCESSING: List[str] = [
    'convert_image_to_base64',
    'check_and_resize_image',
    'estimate_image_tokens',
    'process_image_source',
    'process_multiple_images',
]

CLAUDE_INTEGRATION: List[str] = [
    'claude_vision_analysis',
]

EXCEPTIONS: List[str] = [
    'ClaudeVisionError',
    'InvalidRequestError',
    'AuthenticationError',
    'PermissionError',
    'NotFoundError',
    'RateLimitError',
    'APIError',
    'OverloadedError',
]

CONFIGURATION: List[str] = [
    'Configuration',
]

ADVANCED_FEATURES: List[str] = [
    'visual_judge',
    'image_evolution_analyzer',
    'persona_based_analysis',
    'comparative_time_series_analysis',
    'generate_alt_text',
]

UTILITIES: List[str] = [
    'logger',
]

# Combine all categories
__all__: List[str] = (
    IMAGE_PROCESSING +
    CLAUDE_INTEGRATION +
    EXCEPTIONS +
    CONFIGURATION +
    ADVANCED_FEATURES +
    UTILITIES
)