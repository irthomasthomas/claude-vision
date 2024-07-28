# image_processing.py
from .image_processing import (
    convert_image_to_base64,
    check_and_resize_image,
    estimate_image_tokens,
    process_image_source,
    process_multiple_images
)

# claude_integration.py
from .claude_integration import claude_vision_analysis

# exceptions.py
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

# config.py
from .config import (
    ANTHROPIC_API_KEY,
    DEFAULT_PROMPT,
    MAX_IMAGE_SIZE,
    SUPPORTED_FORMATS,
    DEFAULT_PERSONAS,
    DEFAULT_STYLES
)

# advanced_features.py
from .advanced_features import (
    visual_judge,
    image_evolution_analyzer,
    persona_based_analysis,
    comparative_time_series_analysis,
    generate_alt_text
)

# utils.py
from .utils import logger

__all__ = [
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
    'ANTHROPIC_API_KEY',
    'DEFAULT_PROMPT',
    'MAX_IMAGE_SIZE',
    'SUPPORTED_FORMATS',
    'DEFAULT_PERSONAS',
    'DEFAULT_STYLES',
    
    # Advanced features
    'visual_judge',
    'image_evolution_analyzer',
    'persona_based_analysis',
    'comparative_time_series_analysis',
    'generate_alt_text',
    
    # Utilities
    'logger'
]