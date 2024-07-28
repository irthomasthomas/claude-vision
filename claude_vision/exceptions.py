from enum import Enum
from typing import Optional

class AnthropicErrorType(Enum):
    INVALID_REQUEST = "Invalid request"
    AUTHENTICATION = "Authentication error"
    PERMISSION = "Permission error"
    NOT_FOUND = "Resource not found"
    RATE_LIMIT = "Rate limit exceeded"
    API_ERROR = "API error"
    OVERLOADED = "Service temporarily overloaded"

class AnthropicError(Exception):
    """Base exception class for Anthropic API errors."""
    def __init__(self, error_type: AnthropicErrorType, message: Optional[str] = None):
        self.error_type = error_type
        self.message = message or error_type.value
        super().__init__(self.message)

    def __str__(self) -> str:
        return f"{self.error_type.name}: {self.message}"

class InvalidRequestError(AnthropicError):
    """Exception raised for invalid requests."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.INVALID_REQUEST, message)

class AuthenticationError(AnthropicError):
    """Exception raised for authentication errors."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.AUTHENTICATION, message)

class PermissionError(AnthropicError):
    """Exception raised for permission-related errors."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.PERMISSION, message)

class NotFoundError(AnthropicError):
    """Exception raised when a requested resource is not found."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.NOT_FOUND, message)

class RateLimitError(AnthropicError):
    """Exception raised when rate limits are exceeded."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.RATE_LIMIT, message)

class APIError(AnthropicError):
    """Exception raised for general API errors."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.API_ERROR, message)

class OverloadedError(AnthropicError):
    """Exception raised when the API is temporarily overloaded."""
    def __init__(self, message: Optional[str] = None):
        super().__init__(AnthropicErrorType.OVERLOADED, message)