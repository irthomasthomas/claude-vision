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

def create_error_class(error_type: AnthropicErrorType) -> type:
    """Factory function to create specific error classes."""
    class_name = f"{error_type.name.capitalize()}Error"
    return type(class_name, (AnthropicError,), {
        '__init__': lambda self, message=None: AnthropicError.__init__(self, error_type, message)
    })

# Create specific error classes
InvalidRequestError = create_error_class(AnthropicErrorType.INVALID_REQUEST)
AuthenticationError = create_error_class(AnthropicErrorType.AUTHENTICATION)
PermissionError = create_error_class(AnthropicErrorType.PERMISSION)
NotFoundError = create_error_class(AnthropicErrorType.NOT_FOUND)
RateLimitError = create_error_class(AnthropicErrorType.RATE_LIMIT)
APIError = create_error_class(AnthropicErrorType.API_ERROR)
OverloadedError = create_error_class(AnthropicErrorType.OVERLOADED)