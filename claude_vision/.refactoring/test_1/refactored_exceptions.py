from enum import Enum

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
    def __init__(self, error_type: AnthropicErrorType, message: str = None):
        self.error_type = error_type
        self.message = message or error_type.value
        super().__init__(self.message)

    def __str__(self):
        return f"{self.error_type.name}: {self.message}"

class InvalidRequestError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.INVALID_REQUEST, message)

class AuthenticationError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.AUTHENTICATION, message)

class PermissionError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.PERMISSION, message)

class NotFoundError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.NOT_FOUND, message)

class RateLimitError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.RATE_LIMIT, message)

class APIError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.API_ERROR, message)

class OverloadedError(AnthropicError):
    def __init__(self, message: str = None):
        super().__init__(AnthropicErrorType.OVERLOADED, message)