"""
Comprehensive Error Handling for Zoho CRM API
Maps Zoho-specific error codes to meaningful exceptions
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# EXCEPTION CLASSES
# ============================================================================

class ZohoAPIError(Exception):
    """Base exception for Zoho API errors."""
    def __init__(self, message: str, code: Optional[str] = None, details: Optional[Dict] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}


class ZohoRateLimitError(ZohoAPIError):
    """Raised when rate limit is exceeded (HTTP 429)."""
    pass


class ZohoNotFoundError(ZohoAPIError):
    """Raised when resource is not found (HTTP 404)."""
    pass


class ZohoValidationError(ZohoAPIError):
    """Raised when request validation fails (HTTP 400, 422)."""
    pass


class ZohoAuthenticationError(ZohoAPIError):
    """Raised on authentication failures (HTTP 401, INVALID_OAUTHTOKEN)."""
    pass


class ZohoPermissionError(ZohoAPIError):
    """Raised on permission/authorization failures (HTTP 403)."""
    pass


class ZohoDuplicateDataError(ZohoAPIError):
    """Raised when duplicate data is detected."""
    pass


class ZohoRecordLockedError(ZohoAPIError):
    """Raised when trying to modify a locked record."""
    pass


class ZohoPartialSuccessError(ZohoAPIError):
    """Raised when some records succeed but others fail (HTTP 207)."""
    def __init__(self, message: str, success_records: list, failed_records: list):
        super().__init__(message)
        self.success_records = success_records
        self.failed_records = failed_records


# ============================================================================
# ZOHO ERROR CODE MAPPINGS
# ============================================================================

ZOHO_ERROR_CODES = {
    # Authentication Errors
    "INVALID_TOKEN": "Access token is invalid or expired",
    "INVALID_OAUTHTOKEN": "OAuth token is invalid or expired",
    "AUTHENTICATION_FAILURE": "Authentication failed - check credentials",
    "OAUTH_SCOPE_MISMATCH": "OAuth scope mismatch - insufficient permissions",

    # Authorization Errors
    "NO_PERMISSION": "No permission to perform this operation",
    "PERMISSION_DENIED": "Permission denied for this resource",
    "FORBIDDEN": "Access to this resource is forbidden",

    # Data Errors
    "DUPLICATE_DATA": "Duplicate data - record already exists with same unique field value",
    "MANDATORY_NOT_FOUND": "Mandatory field missing in request",
    "INVALID_DATA": "Invalid data format or value",
    "INVALID_MODULE": "Invalid module name specified",
    "INVALID_REQUEST": "Invalid request structure",

    # Record State Errors
    "RECORD_LOCKED": "Record is locked and cannot be modified",
    "RECORD_IN_BLUEPRINT": "Record is in blueprint state",
    "RECORD_NOT_FOUND": "Record not found with specified ID",

    # Limit Errors
    "API_LIMIT_EXCEEDED": "API call limit exceeded",
    "TOO_MANY_REQUESTS": "Too many requests - rate limit exceeded",
    "QUERY_LIMIT_EXCEEDED": "Query returned too many results",
    "FILE_SIZE_EXCEEDED": "File size exceeds maximum limit (HTTP 413)",

    # Operation Errors
    "UNABLE_TO_PARSE_DATA_TYPE": "Unable to parse data type",
    "PATTERN_NOT_MATCHED": "Field value doesn't match required pattern",
    "INTERNAL_ERROR": "Internal server error occurred",
}


# ============================================================================
# ERROR PARSING AND HANDLING
# ============================================================================

def parse_zoho_error(response_data: Dict[str, Any], status_code: int) -> ZohoAPIError:
    """
    Parse Zoho API error response and return appropriate exception.

    Args:
        response_data: JSON response from Zoho API
        status_code: HTTP status code

    Returns:
        ZohoAPIError: Appropriate exception for the error
    """
    # Extract error information
    error_code = None
    error_message = "Unknown error"
    error_details = {}

    # Try to extract from 'data' array (common format)
    if 'data' in response_data and isinstance(response_data['data'], list) and len(response_data['data']) > 0:
        error_item = response_data['data'][0]
        if isinstance(error_item, dict):
            error_code = error_item.get('code')
            error_message = error_item.get('message', error_message)
            error_details = error_item.get('details', {})

    # Try direct keys
    if not error_code:
        error_code = response_data.get('code')
        error_message = response_data.get('message', error_message)

    # Enhance message with known error code descriptions
    if error_code and error_code in ZOHO_ERROR_CODES:
        enhanced_message = f"{ZOHO_ERROR_CODES[error_code]}: {error_message}"
    else:
        enhanced_message = error_message

    # Map to appropriate exception based on code and status
    if error_code in ('INVALID_TOKEN', 'INVALID_OAUTHTOKEN', 'AUTHENTICATION_FAILURE'):
        return ZohoAuthenticationError(enhanced_message, error_code, error_details)

    elif error_code in ('NO_PERMISSION', 'PERMISSION_DENIED', 'FORBIDDEN', 'OAUTH_SCOPE_MISMATCH'):
        return ZohoPermissionError(enhanced_message, error_code, error_details)

    elif error_code == 'DUPLICATE_DATA':
        return ZohoDuplicateDataError(enhanced_message, error_code, error_details)

    elif error_code == 'RECORD_LOCKED':
        return ZohoRecordLockedError(enhanced_message, error_code, error_details)

    elif error_code in ('API_LIMIT_EXCEEDED', 'TOO_MANY_REQUESTS') or status_code == 429:
        return ZohoRateLimitError(enhanced_message, error_code, error_details)

    elif status_code == 404 or error_code == 'RECORD_NOT_FOUND':
        return ZohoNotFoundError(enhanced_message, error_code, error_details)

    elif status_code in (400, 422) or error_code in ('MANDATORY_NOT_FOUND', 'INVALID_DATA', 'PATTERN_NOT_MATCHED'):
        return ZohoValidationError(enhanced_message, error_code, error_details)

    # Generic error
    return ZohoAPIError(enhanced_message, error_code, error_details)


def handle_partial_success(response_data: Dict[str, Any]) -> None:
    """
    Check for partial success (HTTP 207) and raise if found.

    Args:
        response_data: JSON response from Zoho API

    Raises:
        ZohoPartialSuccessError: If some records failed
    """
    if 'data' not in response_data or not isinstance(response_data['data'], list):
        return

    success_records = []
    failed_records = []

    for record in response_data['data']:
        if not isinstance(record, dict):
            continue

        code = record.get('code', '').upper()
        status = record.get('status', '').lower()

        if code == 'SUCCESS' or status == 'success':
            success_records.append(record)
        elif code in ('ERROR', 'FAILED') or status in ('error', 'failed'):
            failed_records.append(record)

    # If we have both successes and failures, it's a partial success
    if success_records and failed_records:
        error_messages = []
        for failed in failed_records:
            msg = failed.get('message', 'Unknown error')
            record_id = failed.get('details', {}).get('id', 'Unknown')
            error_messages.append(f"Record {record_id}: {msg}")

        raise ZohoPartialSuccessError(
            message=f"{len(failed_records)} record(s) failed: {'; '.join(error_messages)}",
            success_records=success_records,
            failed_records=failed_records
        )


def format_error_message(response: Dict[str, Any]) -> str:
    """
    Extract and format error message from Zoho API error response.

    Args:
        response: Zoho error response

    Returns:
        str: Formatted error message
    """
    try:
        if 'data' in response and isinstance(response['data'], list) and len(response['data']) > 0:
            error = response['data'][0]
            if isinstance(error, dict) and 'message' in error:
                code = error.get('code', 'UNKNOWN')
                message = error['message']

                # Add enhanced description if we have it
                if code in ZOHO_ERROR_CODES:
                    return f"[{code}] {ZOHO_ERROR_CODES[code]}: {message}"
                return f"[{code}] {message}"

        if 'message' in response:
            return response['message']

        return str(response)

    except Exception:
        return "Unknown error occurred"


# ============================================================================
# ERROR RECOVERY HELPERS
# ============================================================================

def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error should be retried.

    Args:
        error: Exception that occurred

    Returns:
        bool: True if error is retryable
    """
    # Rate limit errors should be retried with backoff
    if isinstance(error, ZohoRateLimitError):
        return True

    # Authentication errors might be retryable after token refresh
    if isinstance(error, ZohoAuthenticationError):
        return True

    # Generic API errors might be transient
    if isinstance(error, ZohoAPIError) and error.code in ('INTERNAL_ERROR', 'UNABLE_TO_PARSE_DATA_TYPE'):
        return True

    # Don't retry validation or permission errors
    if isinstance(error, (ZohoValidationError, ZohoPermissionError, ZohoDuplicateDataError, ZohoRecordLockedError)):
        return False

    return False


def get_retry_delay(error: Exception, attempt: int) -> int:
    """
    Get recommended retry delay in seconds.

    Args:
        error: Exception that occurred
        attempt: Retry attempt number (1-indexed)

    Returns:
        int: Delay in seconds
    """
    # Rate limit errors: exponential backoff starting at 60s
    if isinstance(error, ZohoRateLimitError):
        return min(60 * (2 ** (attempt - 1)), 600)  # Max 10 minutes

    # Auth errors: short delay (token refresh)
    if isinstance(error, ZohoAuthenticationError):
        return 2

    # Other retryable errors: standard exponential backoff
    return min(2 ** attempt, 30)  # Max 30 seconds
