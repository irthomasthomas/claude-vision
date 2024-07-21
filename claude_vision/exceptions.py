class AnthropicError(Exception):
    """Base exception class for Anthropic API errors."""
    pass

class InvalidRequestError(AnthropicError):
    """Exception raised for invalid requests."""
    pass

class AuthenticationError(AnthropicError):
    """Exception raised for authentication errors."""
    pass

class PermissionError(AnthropicError):
    """Exception raised for permission-related errors."""
    pass

class NotFoundError(AnthropicError):
    """Exception raised when a requested resource is not found."""
    pass

class RateLimitError(AnthropicError):
    """Exception raised when rate limits are exceeded."""
    pass

class APIError(AnthropicError):
    """Exception raised for general API errors."""
    pass

class OverloadedError(AnthropicError):
    """Exception raised when the API is temporarily overloaded."""
    pass