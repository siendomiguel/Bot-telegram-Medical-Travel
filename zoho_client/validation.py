"""
Validation helpers for Zoho CRM API requests

Validates requests before sending to API to catch errors early.
"""

from typing import Any, Dict, List
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# ZOHO API LIMITS (from official documentation)
# ============================================================================

MAX_RECORDS_PER_BATCH = 100  # insert, update, delete, upsert
MAX_SEARCH_CRITERIA = 10  # Max criteria in search query
MAX_RELATED_RECORDS_PER_CALL = 100  # Related records operations


# ============================================================================
# VALIDATION FUNCTIONS
# ============================================================================

def validate_batch_size(records: List[Any], operation: str = "operation") -> None:
    """
    Validate that batch size doesn't exceed Zoho's limits.

    Args:
        records: List of records
        operation: Operation name (for error message)

    Raises:
        ValueError: If batch size exceeds limit
    """
    if not isinstance(records, list):
        raise ValueError(f"{operation} requires a list of records")

    count = len(records)
    if count > MAX_RECORDS_PER_BATCH:
        raise ValueError(
            f"{operation} batch size ({count}) exceeds Zoho limit of {MAX_RECORDS_PER_BATCH} records per call. "
            f"Please split into multiple batches."
        )

    if count == 0:
        logger.warning(f"{operation} called with empty records list")


def validate_required_fields(data: Dict[str, Any], required_fields: List[str], module: str) -> None:
    """
    Validate that required fields are present.

    Args:
        data: Record data
        required_fields: List of required field names
        module: Module name (for error message)

    Raises:
        ValueError: If required fields are missing
    """
    missing = []
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == "":
            missing.append(field)

    if missing:
        raise ValueError(
            f"Missing required fields for {module}: {', '.join(missing)}"
        )


def validate_module_name(module: str) -> bool:
    """
    Validate if module name is a standard Zoho CRM module.

    Args:
        module: Module name to validate

    Returns:
        bool: True if valid module

    Note: This only validates standard modules. Custom modules are also supported.
    """
    standard_modules = {
        "Leads", "Contacts", "Accounts", "Deals", "Products",
        "Quotes", "Sales_Orders", "Purchase_Orders", "Invoices",
        "Vendors", "Tasks", "Events", "Calls", "Cases",
        "Solutions", "Campaigns", "Price_Books"
    }

    if module not in standard_modules:
        logger.warning(f"'{module}' is not a standard Zoho module (may be custom module)")

    return True  # Allow custom modules


def validate_search_criteria_count(criteria_string: str) -> None:
    """
    Validate that search criteria doesn't exceed Zoho's limit of 10 criteria.

    Args:
        criteria_string: Zoho criteria string

    Raises:
        ValueError: If too many criteria
    """
    # Count criteria by counting opening parentheses for field conditions
    # Format: (field:operator:value)
    import re

    # Match field criteria patterns: (FieldName:operator:value)
    criteria_matches = re.findall(r'\([A-Za-z_][A-Za-z0-9_]*:[a-z_]+:[^)]+\)', criteria_string)
    criteria_count = len(criteria_matches)

    if criteria_count > MAX_SEARCH_CRITERIA:
        raise ValueError(
            f"Search criteria count ({criteria_count}) exceeds Zoho limit of {MAX_SEARCH_CRITERIA}. "
            f"Please simplify your search."
        )


def validate_duplicate_check_fields(fields: List[str], module: str) -> None:
    """
    Validate duplicate check fields for upsert operation.

    Args:
        fields: List of field names to check for duplicates
        module: Module name

    Raises:
        ValueError: If fields are invalid
    """
    if not fields:
        logger.info(f"No duplicate check fields specified for {module} upsert - using system defaults")
        return

    if not isinstance(fields, list):
        raise ValueError("duplicate_check_fields must be a list")

    if len(fields) == 0:
        logger.warning("Empty duplicate_check_fields list provided")


def validate_email(email: str) -> bool:
    """
    Basic email validation.

    Args:
        email: Email address to validate

    Returns:
        bool: True if email format is valid
    """
    import re

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Basic phone validation (allows various formats).

    Args:
        phone: Phone number to validate

    Returns:
        bool: True if phone format is reasonable
    """
    import re

    # Remove common separators
    cleaned = re.sub(r'[\s\-\(\)\+]', '', phone)

    # Check if it's mostly digits (allow for country codes)
    return len(cleaned) >= 7 and cleaned.replace('+', '').isdigit()


def validate_date_format(date_string: str) -> bool:
    """
    Validate date string format (YYYY-MM-DD or with time).

    Args:
        date_string: Date string to validate

    Returns:
        bool: True if format is valid
    """
    import re

    # Accept various date formats
    patterns = [
        r'^\d{4}-\d{2}-\d{2}$',  # YYYY-MM-DD
        r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}',  # ISO datetime
        r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',  # Space-separated datetime
    ]

    return any(re.match(pattern, date_string) for pattern in patterns)


# ============================================================================
# BULK OPERATION HELPERS
# ============================================================================

def chunk_records(records: List[Dict[str, Any]], chunk_size: int = MAX_RECORDS_PER_BATCH) -> List[List[Dict[str, Any]]]:
    """
    Split records into chunks for batch operations.

    Args:
        records: List of all records
        chunk_size: Maximum records per chunk (default: 100)

    Returns:
        List[List[Dict]]: List of record chunks

    Example:
        >>> records = [{"name": f"Record {i}"} for i in range(250)]
        >>> chunks = chunk_records(records)
        >>> len(chunks)
        3
        >>> len(chunks[0])
        100
        >>> len(chunks[2])
        50
    """
    chunk_size = min(chunk_size, MAX_RECORDS_PER_BATCH)

    if len(records) <= chunk_size:
        return [records]

    chunks = []
    for i in range(0, len(records), chunk_size):
        chunks.append(records[i:i + chunk_size])

    logger.info(f"Split {len(records)} records into {len(chunks)} chunks of max {chunk_size}")
    return chunks


def validate_record_ids(record_ids: List[str]) -> None:
    """
    Validate list of record IDs.

    Args:
        record_ids: List of record IDs

    Raises:
        ValueError: If IDs are invalid
    """
    if not isinstance(record_ids, list):
        raise ValueError("record_ids must be a list")

    if len(record_ids) == 0:
        raise ValueError("record_ids list is empty")

    # Check for valid ID format (Zoho IDs are numeric strings)
    for record_id in record_ids:
        if not isinstance(record_id, (str, int)):
            raise ValueError(f"Invalid record ID type: {type(record_id)}")

        if isinstance(record_id, str) and not record_id.strip():
            raise ValueError("Empty record ID found")


# ============================================================================
# MODULE-SPECIFIC REQUIRED FIELDS
# ============================================================================

REQUIRED_FIELDS_BY_MODULE = {
    "Leads": ["Last_Name"],
    "Contacts": ["Last_Name"],
    "Accounts": ["Account_Name"],
    "Deals": ["Deal_Name", "Stage"],
    "Products": ["Product_Name"],
    "Vendors": ["Vendor_Name"],
    "Tasks": ["Subject"],
    "Events": ["Event_Title", "Start_DateTime", "End_DateTime"],
    "Calls": ["Subject", "Call_Type"],
}


def get_required_fields(module: str) -> List[str]:
    """
    Get required fields for a module.

    Args:
        module: Module name

    Returns:
        List[str]: Required field names
    """
    return REQUIRED_FIELDS_BY_MODULE.get(module, [])


def validate_record_for_module(module: str, data: Dict[str, Any]) -> None:
    """
    Validate record data for a specific module.

    Args:
        module: Module name
        data: Record data

    Raises:
        ValueError: If validation fails
    """
    required_fields = get_required_fields(module)
    if required_fields:
        validate_required_fields(data, required_fields, module)
