Here's a refactored version of the exceptions code:

<REFACTORED_CODE>
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
</REFACTORED_CODE>

<REVIEW>
The refactored code introduces several improvements:

1. A base `ClaudeVisionError` class: This replaces the `AnthropicError` class and serves as the parent for all custom exceptions. It provides a consistent structure for all errors.

2. `ErrorCode` enum: This new enum class defines error codes for each type of error, improving error categorization and making it easier to handle errors programmatically.

3. Consistent error structure: Each error class now inherits from `ClaudeVisionError` and sets its specific error code. This provides a uniform way to create and handle errors.

4. Renamed `PermissionError` to `PermissionDeniedError`: This avoids naming conflicts with Python's built-in `PermissionError`.

5. Improved type hinting: The `message` parameter in each exception class is explicitly typed as `str`.

6. Consistent docstrings: Each exception class maintains its descriptive docstring.

These changes make the error handling more robust, consistent, and easier to use throughout the Claude Vision package. It also allows for future expansion of error types and codes if needed.
</REVIEW>