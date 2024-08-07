from typing import List
from .core import (
    # Image processing
    convert_image_to_base64,
    check_and_resize_image,
    estimate_image_tokens,
    process_image_source,
    process_multiple_images,
    
    # Claude integration
    claude_vision_analysis,
    
    # Exceptions
    ClaudeVisionError,
    InvalidRequestError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    APIError,
    OverloadedError,
    
    # Configuration
    Configuration,
    
    # Advanced features
    visual_judge,
    image_evolution_analyzer,
    persona_based_analysis,
    comparative_time_series_analysis,
    
    # Utilities
    logger
)

# Initialize configuration
config = Configuration()

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
    'config',
]

ADVANCED_FEATURES: List[str] = [
    'visual_judge',
    'image_evolution_analyzer',
    'persona_based_analysis',
    'comparative_time_series_analysis',
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