"""
Advanced Pagination Support for Zoho CRM API

Handles both page/per_page (first 2,000 records) and page_token (beyond 2,000).
"""

from typing import Any, Dict, List, Optional, AsyncIterator
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# PAGINATION CONSTANTS
# ============================================================================

# Zoho CRM pagination limits (from official documentation)
MAX_RECORDS_PER_PAGE = 200
MAX_RECORDS_WITH_PAGE_NUMBER = 2000  # After this, must use page_token
MAX_RECORDS_TOTAL = 100000  # Absolute maximum retrievable
PAGE_TOKEN_EXPIRY_HOURS = 24  # Page tokens expire after 24 hours


# ============================================================================
# PAGINATION HELPER FUNCTIONS
# ============================================================================

def needs_page_token(total_fetched: int) -> bool:
    """
    Determine if page_token is needed for pagination.

    Args:
        total_fetched: Total records fetched so far

    Returns:
        bool: True if page_token required
    """
    return total_fetched >= MAX_RECORDS_WITH_PAGE_NUMBER


def build_pagination_params(
    page: Optional[int] = None,
    per_page: int = MAX_RECORDS_PER_PAGE,
    page_token: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build pagination parameters for Zoho API request.

    Args:
        page: Page number (1-indexed, for first 2,000 records only)
        per_page: Records per page (max 200)
        page_token: Token for records beyond 2,000

    Returns:
        Dict: Pagination parameters

    Raises:
        ValueError: If invalid parameters provided
    """
    params = {}

    # Enforce max per_page
    per_page = min(per_page, MAX_RECORDS_PER_PAGE)
    params["per_page"] = per_page

    # Use page_token OR page number (mutually exclusive)
    if page_token:
        # Using token-based pagination (beyond 2,000 records)
        params["page_token"] = page_token
        logger.debug(f"Using page_token pagination (token: {page_token[:10]}...)")

    elif page:
        # Using page number (first 2,000 records)
        if page < 1:
            raise ValueError("Page number must be >= 1")

        # Warn if trying to use page number beyond limit
        estimated_records = page * per_page
        if estimated_records > MAX_RECORDS_WITH_PAGE_NUMBER:
            logger.warning(
                f"Page {page} with {per_page} per_page may exceed 2,000 record limit. "
                f"Consider using page_token pagination instead."
            )

        params["page"] = page
        logger.debug(f"Using page number pagination (page: {page}, per_page: {per_page})")

    else:
        # Default to page 1
        params["page"] = 1

    return params


def extract_next_page_token(response: Dict[str, Any]) -> Optional[str]:
    """
    Extract next page token from Zoho API response.

    Args:
        response: Zoho API response

    Returns:
        Optional[str]: Next page token if available
    """
    if not isinstance(response, dict):
        return None

    # Check in 'info' section
    info = response.get("info", {})
    if isinstance(info, dict):
        next_token = info.get("next_page_token")
        if next_token:
            logger.debug(f"Found next_page_token: {next_token[:10]}...")
            return next_token

    return None


def has_more_records(response: Dict[str, Any]) -> bool:
    """
    Check if there are more records to fetch.

    Args:
        response: Zoho API response

    Returns:
        bool: True if more records available
    """
    if not isinstance(response, dict):
        return False

    info = response.get("info", {})
    if isinstance(info, dict):
        # Check 'more_records' flag
        more_records = info.get("more_records", False)
        if more_records:
            return True

        # Check for next_page_token
        if info.get("next_page_token"):
            return True

    return False


def get_record_count(response: Dict[str, Any]) -> int:
    """
    Get number of records in current response.

    Args:
        response: Zoho API response

    Returns:
        int: Number of records
    """
    if not isinstance(response, dict):
        return 0

    data = response.get("data", [])
    if isinstance(data, list):
        return len(data)

    info = response.get("info", {})
    if isinstance(info, dict) and "count" in info:
        return int(info["count"])

    return 0


# ============================================================================
# PAGINATION ITERATOR
# ============================================================================

class PaginationIterator:
    """
    Async iterator for paginating through Zoho CRM records.

    Automatically handles transition from page numbers to page_token.

    Usage:
        async for page_records in PaginationIterator(client, "/Leads", params):
            process(page_records)
    """

    def __init__(
        self,
        client: Any,  # ZohoBaseClient
        endpoint: str,
        base_params: Optional[Dict[str, Any]] = None,
        max_records: Optional[int] = None
    ):
        """
        Initialize pagination iterator.

        Args:
            client: ZohoBaseClient instance with get() method
            endpoint: API endpoint (e.g., "/Leads")
            base_params: Base parameters (fields, sort_by, etc.)
            max_records: Maximum records to fetch (None for all)
        """
        self.client = client
        self.endpoint = endpoint
        self.base_params = base_params or {}
        self.max_records = min(max_records, MAX_RECORDS_TOTAL) if max_records else MAX_RECORDS_TOTAL

        self.total_fetched = 0
        self.current_page = 1
        self.page_token: Optional[str] = None
        self.done = False

    def __aiter__(self):
        """Return self as async iterator."""
        return self

    async def __anext__(self) -> List[Dict[str, Any]]:
        """
        Fetch next page of records.

        Returns:
            List[Dict]: Records from current page

        Raises:
            StopAsyncIteration: When no more records
        """
        if self.done or self.total_fetched >= self.max_records:
            raise StopAsyncIteration

        # Build pagination params
        if self.page_token:
            # Use page_token for records beyond 2,000
            pagination_params = build_pagination_params(page_token=self.page_token)
        else:
            # Use page number for first 2,000 records
            pagination_params = build_pagination_params(
                page=self.current_page,
                per_page=min(MAX_RECORDS_PER_PAGE, self.max_records - self.total_fetched)
            )

        # Merge with base params
        request_params = {**self.base_params, **pagination_params}

        # Make request
        try:
            response = await self.client.get(self.endpoint, params=request_params)
        except Exception as e:
            logger.error(f"Error fetching page: {e}")
            raise StopAsyncIteration

        # Extract records
        records = response.get("data", [])
        if not isinstance(records, list):
            records = []

        # Update counters
        records_count = len(records)
        self.total_fetched += records_count

        logger.info(f"Fetched {records_count} records (total: {self.total_fetched}/{self.max_records})")

        # Check if more records available
        if has_more_records(response):
            # Get next page token
            next_token = extract_next_page_token(response)

            if next_token:
                # Switch to page_token pagination
                self.page_token = next_token
                logger.info(f"Switching to page_token pagination (fetched {self.total_fetched} records)")
            else:
                # Continue with page number
                self.current_page += 1

        else:
            # No more records
            self.done = True
            logger.info(f"Pagination complete. Total records fetched: {self.total_fetched}")

        # Check if we've hit our limit
        if self.total_fetched >= self.max_records:
            self.done = True

        # If no records returned, we're done
        if records_count == 0:
            self.done = True
            raise StopAsyncIteration

        return records


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

async def fetch_all_records(
    client: Any,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    max_records: Optional[int] = None
) -> List[Dict[str, Any]]:
    """
    Fetch all records from an endpoint with automatic pagination.

    Args:
        client: ZohoBaseClient instance
        endpoint: API endpoint
        params: Base parameters (fields, sort_by, etc.)
        max_records: Maximum records to fetch

    Returns:
        List[Dict]: All fetched records

    Example:
        >>> records = await fetch_all_records(client, "/Leads", {"fields": "id,Full_Name,Email"})
    """
    all_records = []

    async for page_records in PaginationIterator(client, endpoint, params, max_records):
        all_records.extend(page_records)

    return all_records


async def count_all_records(
    client: Any,
    module: str
) -> int:
    """
    Get total count of records in a module.

    Uses the record count API endpoint.

    Args:
        client: ZohoBaseClient instance
        module: Module name (e.g., "Leads")

    Returns:
        int: Total record count

    Example:
        >>> total = await count_all_records(client, "Leads")
    """
    try:
        response = await client.get(f"/{module}/actions/count")
        count = response.get("count", 0)
        logger.info(f"Total {module} count: {count}")
        return int(count)
    except Exception as e:
        logger.error(f"Error getting record count: {e}")
        return 0
