from enum import Enum

class ErrorCode(Enum):
    INVALID_REQUEST = "invalid_request"
    AUTHENTICATION = "authentication"
    PERMISSION = "permission"
    NOT_FOUND = "not_found"
    RATE_LIMIT = "rate_limit"
    API_ERROR = "api_error"
    OVERLOADED = "overloaded"

class ClaudeVisionError(Exception):
    """Base exception class for Claude Vision API errors."""
    def __init__(self, message: str, error_code: ErrorCode):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class InvalidRequestError(ClaudeVisionError):
    """Exception raised for invalid requests."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.INVALID_REQUEST)

class AuthenticationError(ClaudeVisionError):
    """Exception raised for authentication errors."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.AUTHENTICATION)

class PermissionDeniedError(ClaudeVisionError):
    """Exception raised for permission-related errors."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.PERMISSION)

class NotFoundError(ClaudeVisionError):
    """Exception raised when a requested resource is not found."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.NOT_FOUND)

class RateLimitError(ClaudeVisionError):
    """Exception raised when rate limits are exceeded."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.RATE_LIMIT)

class APIError(ClaudeVisionError):
    """Exception raised for general API errors."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.API_ERROR)

class OverloadedError(ClaudeVisionError):
    """Exception raised when the API is temporarily overloaded."""
    def __init__(self, message: str):
        super().__init__(message, ErrorCode.OVERLOADED)