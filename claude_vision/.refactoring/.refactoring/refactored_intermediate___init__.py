from typing import List, Dict, Any

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
    AnthropicError,
    InvalidRequestError,
    AuthenticationError,
    PermissionError,
    NotFoundError,
    RateLimitError,
    APIError,
    OverloadedError
)

# Configuration
from .config import Config

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

__all__: List[str] = [
    # Image processing
    'convert_image_to_base64',
    'check_and_resize_image',
    'estimate_image_tokens',
    'process_image_source',
    'process_multiple_images',
    
    # Claude integration
    'claude_vision_analysis',
    
    # Exceptions
    'AnthropicError',
    'InvalidRequestError',
    'AuthenticationError',
    'PermissionError',
    'NotFoundError',
    'RateLimitError',
    'APIError',
    'OverloadedError',
    
    # Configuration
    'Config',
    
    # Advanced features
    'visual_judge',
    'image_evolution_analyzer',
    'persona_based_analysis',
    'comparative_time_series_analysis',
    'generate_alt_text',
    
    # Utilities
    'logger'
]

# Initialize configuration
config = Config()

# Make configuration values available at module level
ANTHROPIC_API_KEY: str = config.ANTHROPIC_API_KEY
DEFAULT_PROMPT: str = config.DEFAULT_PROMPT
MAX_IMAGE_SIZE: tuple = config.MAX_IMAGE_SIZE
SUPPORTED_FORMATS: List[str] = config.SUPPORTED_FORMATS
DEFAULT_PERSONAS: Dict[str, str] = config.DEFAULT_PERSONAS
DEFAULT_STYLES: Dict[str, Any] = config.DEFAULT_STYLES