"""
Tool schemas for all 109 Zoho CRM tools in OpenAI-compatible JSON format.
Used by OpenRouter's API for function calling.

Auto-generated from main.py and advanced_tools.py
"""

TOOL_DEFINITIONS = [
    # ========================================================================
    # LEADS TOOLS (1-5)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_lead",
            "description": "Create a new lead in Zoho CRM. Required: last_name, company.",
            "parameters": {
                "type": "object",
                "properties": {
                    "last_name": {"type": "string", "description": "Last name of the lead"},
                    "company": {"type": "string", "description": "Company name"},
                    "first_name": {"type": "string", "description": "First name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "lead_source": {"type": "string", "description": "Source of the lead (e.g., 'Website', 'Referral')"},
                    "lead_status": {"type": "string", "description": "Lead status (e.g., 'New', 'Contacted', 'Qualified')"},
                    "industry": {"type": "string", "description": "Industry type"}
                },
                "required": ["last_name", "company"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_lead",
            "description": "Get a lead by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string", "description": "The Zoho CRM Lead ID"}
                },
                "required": ["lead_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_lead",
            "description": "Update an existing lead in Zoho CRM. Required: lead_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string", "description": "Lead ID to update"},
                    "first_name": {"type": "string", "description": "New first name"},
                    "last_name": {"type": "string", "description": "New last name"},
                    "email": {"type": "string", "description": "New email"},
                    "phone": {"type": "string", "description": "New phone"},
                    "company": {"type": "string", "description": "New company"},
                    "lead_status": {"type": "string", "description": "New status"},
                    "lead_source": {"type": "string", "description": "New source"}
                },
                "required": ["lead_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_lead",
            "description": "Delete a lead from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string", "description": "Lead ID to delete"}
                },
                "required": ["lead_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "convert_lead_to_contact",
            "description": "Convert a Lead to Contact (and optionally Account/Deal).",
            "parameters": {
                "type": "object",
                "properties": {
                    "lead_id": {"type": "string", "description": "Lead ID to convert"},
                    "create_account": {"type": "boolean", "description": "Create an Account (default True)"},
                    "create_deal": {"type": "boolean", "description": "Create a Deal (default False)"}
                },
                "required": ["lead_id"]
            }
        }
    },

    # ========================================================================
    # SEARCH TOOLS (6-10)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "search_leads",
            "description": "Search for leads using various criteria. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "last_name": {"type": "string", "description": "Search by last name (contains)"},
                    "email": {"type": "string", "description": "Search by email (contains)"},
                    "phone": {"type": "string", "description": "Search by phone number"},
                    "company": {"type": "string", "description": "Search by company name (contains)"},
                    "lead_status": {"type": "string", "description": "Search by lead status (equals)"},
                    "created_after": {"type": "string", "description": "Search for leads created after date (YYYY-MM-DD)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "count_all_records",
            "description": "Count ALL records in a module using advanced pagination beyond the 2,000 record limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, Accounts, Deals, Products, etc.)"}
                },
                "required": ["module"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_email",
            "description": "Search any module by email address.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module to search (Leads, Contacts, Accounts, etc.)"},
                    "email": {"type": "string", "description": "Email address to search for"}
                },
                "required": ["module", "email"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_phone",
            "description": "Search any module by phone number.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module to search (Leads, Contacts, etc.)"},
                    "phone": {"type": "string", "description": "Phone number to search for"}
                },
                "required": ["module", "phone"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_by_word",
            "description": "Perform a global word search across all fields in a module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module to search (Leads, Contacts, Accounts, Deals, etc.)"},
                    "word": {"type": "string", "description": "Word or phrase to search for"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 20)"}
                },
                "required": ["module", "word"]
            }
        }
    },

    # ========================================================================
    # CONTACT TOOLS (11-15)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_contact",
            "description": "Create a new contact in Zoho CRM. Required: last_name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "last_name": {"type": "string", "description": "Last name (required)"},
                    "first_name": {"type": "string", "description": "First name"},
                    "email": {"type": "string", "description": "Email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "account_name": {"type": "string", "description": "Associated account name"}
                },
                "required": ["last_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_contact",
            "description": "Get a contact by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string", "description": "The Zoho CRM Contact ID"}
                },
                "required": ["contact_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_contact",
            "description": "Update an existing contact in Zoho CRM. Required: contact_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string", "description": "Contact ID to update"},
                    "first_name": {"type": "string", "description": "New first name"},
                    "last_name": {"type": "string", "description": "New last name"},
                    "email": {"type": "string", "description": "New email"},
                    "phone": {"type": "string", "description": "New phone"},
                    "account_name": {"type": "string", "description": "New account name"}
                },
                "required": ["contact_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_contact",
            "description": "Delete a contact from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "contact_id": {"type": "string", "description": "Contact ID to delete"}
                },
                "required": ["contact_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_contacts",
            "description": "Search for contacts using various criteria. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "last_name": {"type": "string", "description": "Search by last name (contains)"},
                    "email": {"type": "string", "description": "Search by email (contains)"},
                    "phone": {"type": "string", "description": "Search by phone number"},
                    "account_name": {"type": "string", "description": "Search by account name (contains)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # ACCOUNT TOOLS (16-21)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_account",
            "description": "Create a new account in Zoho CRM. Required: account_name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string", "description": "Account name"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "website": {"type": "string", "description": "Website URL"},
                    "industry": {"type": "string", "description": "Industry type"}
                },
                "required": ["account_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_account",
            "description": "Get an account by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "The Zoho CRM Account ID"}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_account",
            "description": "Update an existing account in Zoho CRM. Required: account_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "Account ID to update"},
                    "account_name": {"type": "string", "description": "New account name"},
                    "phone": {"type": "string", "description": "New phone"},
                    "website": {"type": "string", "description": "New website"},
                    "industry": {"type": "string", "description": "New industry"}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_account",
            "description": "Delete an account from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {"type": "string", "description": "Account ID to delete"}
                },
                "required": ["account_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_accounts",
            "description": "Search for accounts using various criteria. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {"type": "string", "description": "Search by account name (contains)"},
                    "phone": {"type": "string", "description": "Search by phone number"},
                    "website": {"type": "string", "description": "Search by website (contains)"},
                    "industry": {"type": "string", "description": "Search by industry (equals)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # DEAL TOOLS (21-26)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_deal",
            "description": "Create a new deal in Zoho CRM. Required: deal_name, stage. To link a contact, provide contact_id (record ID, not name).",
            "parameters": {
                "type": "object",
                "properties": {
                    "deal_name": {"type": "string", "description": "Deal name"},
                    "stage": {"type": "string", "description": "Deal stage (e.g., 'Qualification', 'Proposal/Price Quote', 'Negotiation/Review')"},
                    "amount": {"type": "number", "description": "Deal amount"},
                    "closing_date": {"type": "string", "description": "Expected closing date (YYYY-MM-DD)"},
                    "account_name": {"type": "string", "description": "Associated account name"},
                    "contact_id": {"type": "string", "description": "Associated contact ID (use contact's record ID, not name)"}
                },
                "required": ["deal_name", "stage"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_deal",
            "description": "Get a deal by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deal_id": {"type": "string", "description": "The Zoho CRM Deal ID"}
                },
                "required": ["deal_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_deal",
            "description": "Update an existing deal in Zoho CRM. Required: deal_id. To link a contact, provide contact_id (record ID, not name).",
            "parameters": {
                "type": "object",
                "properties": {
                    "deal_id": {"type": "string", "description": "Deal ID to update"},
                    "deal_name": {"type": "string", "description": "New deal name"},
                    "stage": {"type": "string", "description": "New stage (e.g., 'Qualification', 'Proposal/Price Quote', 'Negotiation/Review', 'Closed Won')"},
                    "amount": {"type": "number", "description": "New amount"},
                    "closing_date": {"type": "string", "description": "New closing date (YYYY-MM-DD)"},
                    "account_name": {"type": "string", "description": "New account name"},
                    "contact_id": {"type": "string", "description": "Contact ID to link (use contact's record ID, not name)"}
                },
                "required": ["deal_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_deal",
            "description": "Delete a deal from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deal_id": {"type": "string", "description": "Deal ID to delete"}
                },
                "required": ["deal_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_deals",
            "description": "Search for deals using various criteria. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "deal_name": {"type": "string", "description": "Search by deal name (contains)"},
                    "stage": {"type": "string", "description": "Search by stage (equals)"},
                    "account_name": {"type": "string", "description": "Search by account name (contains)"},
                    "min_amount": {"type": "number", "description": "Minimum deal amount"},
                    "max_amount": {"type": "number", "description": "Maximum deal amount"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # PRODUCT TOOLS (26-31)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_product",
            "description": "Create a new product in Zoho CRM. Required: product_name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Product name"},
                    "unit_price": {"type": "number", "description": "Product unit price"},
                    "description": {"type": "string", "description": "Product description"},
                    "product_code": {"type": "string", "description": "Product code/SKU"}
                },
                "required": ["product_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product",
            "description": "Get a product by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "The Zoho CRM Product ID"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_product",
            "description": "Update an existing product in Zoho CRM. Required: product_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID to update"},
                    "product_name": {"type": "string", "description": "New product name"},
                    "unit_price": {"type": "number", "description": "New unit price"},
                    "description": {"type": "string", "description": "New description"},
                    "product_code": {"type": "string", "description": "New product code"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_product",
            "description": "Delete a product from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_id": {"type": "string", "description": "Product ID to delete"}
                },
                "required": ["product_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for products using various criteria. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {"type": "string", "description": "Search by product name (contains)"},
                    "product_code": {"type": "string", "description": "Search by product code (equals)"},
                    "min_price": {"type": "number", "description": "Minimum price"},
                    "max_price": {"type": "number", "description": "Maximum price"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # TASK TOOLS (31-39)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_task",
            "description": "Create a task in Zoho CRM. Required: subject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Task subject"},
                    "related_to_id": {"type": "string", "description": "ID of related Lead/Contact/Deal/Account"},
                    "due_date": {"type": "string", "description": "Due date (YYYY-MM-DD)"},
                    "priority": {"type": "string", "description": "Priority: High, Normal, Low (default: Normal)"},
                    "status": {"type": "string", "description": "Status: Not Started, In Progress, Completed, etc. (default: Not Started)"},
                    "description": {"type": "string", "description": "Task description"}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_task",
            "description": "Get a task by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "The Zoho CRM Task ID"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_tasks_for_record",
            "description": "Get all tasks associated with a specific record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, Deals, Accounts)"},
                    "record_id": {"type": "string", "description": "Record ID"}
                },
                "required": ["module", "record_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pending_tasks",
            "description": "Get all tasks for any record with smart auto-detection. Returns ALL tasks (pending, in progress, completed). Works without knowing the module type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_id": {"type": "string", "description": "The ID of any record (Lead, Contact, Deal, or Account)"}
                },
                "required": ["record_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_multiple_leads_for_tasks",
            "description": "Check multiple leads for pending tasks with built-in rate limiting. Use this instead of calling get_pending_tasks multiple times. Max 50 records.",
            "parameters": {
                "type": "object",
                "properties": {
                    "record_ids": {"type": "string", "description": "Comma-separated list of record IDs (e.g., '123,456,789')"}
                },
                "required": ["record_ids"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tasks",
            "description": "Search for tasks with advanced filters. Supports date ranges, status, priority, and subject search.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "description": "Filter by status (e.g., 'Not Started', 'In Progress', 'Completed')"},
                    "priority": {"type": "string", "description": "Filter by priority (High, Normal, Low)"},
                    "due_date_start": {"type": "string", "description": "Tasks due on or after this date (YYYY-MM-DD or YYYY-MM)"},
                    "due_date_end": {"type": "string", "description": "Tasks due on or before this date (YYYY-MM-DD or YYYY-MM)"},
                    "subject_contains": {"type": "string", "description": "Search for tasks with subject containing this text"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 50)"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_task",
            "description": "Update an existing task in Zoho CRM. Required: task_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to update"},
                    "subject": {"type": "string", "description": "New subject"},
                    "status": {"type": "string", "description": "New status (Not Started, In Progress, Completed, etc.)"},
                    "priority": {"type": "string", "description": "New priority (High, Normal, Low)"},
                    "due_date": {"type": "string", "description": "New due date (YYYY-MM-DD)"},
                    "description": {"type": "string", "description": "New description"}
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {"type": "string", "description": "Task ID to delete"}
                },
                "required": ["task_id"]
            }
        }
    },

    # ========================================================================
    # EVENT TOOLS (39-44)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_event",
            "description": "Create an event/meeting in Zoho CRM. Required: event_title, start_datetime, end_datetime.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_title": {"type": "string", "description": "Event title"},
                    "start_datetime": {"type": "string", "description": "Start date and time (YYYY-MM-DD HH:MM:SS)"},
                    "end_datetime": {"type": "string", "description": "End date and time (YYYY-MM-DD HH:MM:SS)"},
                    "related_to_id": {"type": "string", "description": "ID of related Lead/Contact/Deal/Account"},
                    "description": {"type": "string", "description": "Event description"}
                },
                "required": ["event_title", "start_datetime", "end_datetime"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_event",
            "description": "Get an event by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "The Zoho CRM Event ID"}
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_events_for_record",
            "description": "Get all events associated with a specific record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, Deals, Accounts)"},
                    "record_id": {"type": "string", "description": "Record ID"}
                },
                "required": ["module", "record_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_event",
            "description": "Update an existing event in Zoho CRM. Required: event_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID to update"},
                    "event_title": {"type": "string", "description": "New event title"},
                    "start_datetime": {"type": "string", "description": "New start datetime (YYYY-MM-DD HH:MM:SS)"},
                    "end_datetime": {"type": "string", "description": "New end datetime (YYYY-MM-DD HH:MM:SS)"},
                    "description": {"type": "string", "description": "New description"}
                },
                "required": ["event_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_event",
            "description": "Delete an event from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "Event ID to delete"}
                },
                "required": ["event_id"]
            }
        }
    },

    # ========================================================================
    # CALL TOOLS (44-50)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_call",
            "description": "Log a call in Zoho CRM. Required: subject, call_type.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Call subject"},
                    "call_type": {"type": "string", "description": "Call type (Outbound, Inbound, Missed)"},
                    "related_to_id": {"type": "string", "description": "ID of related Lead/Contact/Deal/Account"},
                    "call_start_time": {"type": "string", "description": "Call start time (YYYY-MM-DD HH:MM:SS)"},
                    "call_duration": {"type": "string", "description": "Duration in minutes"},
                    "description": {"type": "string", "description": "Call description/notes"}
                },
                "required": ["subject", "call_type"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_call",
            "description": "Get a call by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string", "description": "The Zoho CRM Call ID"}
                },
                "required": ["call_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_call",
            "description": "Update an existing call log in Zoho CRM. Required: call_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string", "description": "Call ID to update"},
                    "subject": {"type": "string", "description": "New subject"},
                    "call_type": {"type": "string", "description": "New call type"},
                    "call_start_time": {"type": "string", "description": "New start time (YYYY-MM-DD HH:MM:SS)"},
                    "call_duration": {"type": "string", "description": "New duration in minutes"},
                    "description": {"type": "string", "description": "New description"}
                },
                "required": ["call_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_call",
            "description": "Delete a call log from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "call_id": {"type": "string", "description": "Call ID to delete"}
                },
                "required": ["call_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_calls_for_record",
            "description": "Get all calls for a specific record (Lead, Contact, Account, or Deal).",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (e.g., 'Leads', 'Contacts', 'Accounts', 'Deals')"},
                    "record_id": {"type": "string", "description": "The record ID to get calls for"},
                    "limit": {"type": "integer", "description": "Maximum number of calls to return (default: 20)"}
                },
                "required": ["module", "record_id"]
            }
        }
    },

    # ========================================================================
    # NOTE TOOLS (50-54)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_note",
            "description": "Create a note attached to any record. Required: module, record_id, title, content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, Accounts, Deals, etc.)"},
                    "record_id": {"type": "string", "description": "Record ID to attach note to"},
                    "title": {"type": "string", "description": "Note title"},
                    "content": {"type": "string", "description": "Note content"}
                },
                "required": ["module", "record_id", "title", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_notes_for_record",
            "description": "Get all notes for a specific record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, etc.)"},
                    "record_id": {"type": "string", "description": "Record ID"}
                },
                "required": ["module", "record_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_note",
            "description": "Update an existing note. Required: note_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {"type": "string", "description": "Note ID to update"},
                    "title": {"type": "string", "description": "New note title"},
                    "content": {"type": "string", "description": "New note content"}
                },
                "required": ["note_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_note",
            "description": "Delete a note from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "note_id": {"type": "string", "description": "Note ID to delete"}
                },
                "required": ["note_id"]
            }
        }
    },

    # ========================================================================
    # VENDOR TOOLS (54-59)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_vendor",
            "description": "Create a new vendor in Zoho CRM. Required: vendor_name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_name": {"type": "string", "description": "Vendor name"},
                    "email": {"type": "string", "description": "Vendor email address"},
                    "phone": {"type": "string", "description": "Phone number"},
                    "website": {"type": "string", "description": "Vendor website URL"}
                },
                "required": ["vendor_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_vendor",
            "description": "Get a vendor by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "The Zoho CRM Vendor ID"}
                },
                "required": ["vendor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_vendor",
            "description": "Update an existing vendor in Zoho CRM. Required: vendor_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "Vendor ID to update"},
                    "vendor_name": {"type": "string", "description": "New vendor name"},
                    "email": {"type": "string", "description": "New email"},
                    "phone": {"type": "string", "description": "New phone"},
                    "website": {"type": "string", "description": "New website"}
                },
                "required": ["vendor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_vendor",
            "description": "Delete a vendor from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_id": {"type": "string", "description": "Vendor ID to delete"}
                },
                "required": ["vendor_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_vendors",
            "description": "Search for vendors. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "vendor_name": {"type": "string", "description": "Search by vendor name"},
                    "email": {"type": "string", "description": "Search by email"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 10)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # QUOTE TOOLS (59-64)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_quote",
            "description": "Create a new quote in Zoho CRM. Required: subject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Quote subject"},
                    "deal_name": {"type": "string", "description": "Associated deal name"},
                    "account_name": {"type": "string", "description": "Associated account name"},
                    "quote_stage": {"type": "string", "description": "Quote stage (e.g., 'Draft', 'Delivered', 'Accepted')"}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_quote",
            "description": "Get a quote by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string", "description": "The Zoho CRM Quote ID"}
                },
                "required": ["quote_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_quote",
            "description": "Update an existing quote in Zoho CRM. Required: quote_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string", "description": "Quote ID to update"},
                    "subject": {"type": "string", "description": "New subject"},
                    "quote_stage": {"type": "string", "description": "New quote stage"}
                },
                "required": ["quote_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_quote",
            "description": "Delete a quote from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "quote_id": {"type": "string", "description": "Quote ID to delete"}
                },
                "required": ["quote_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_quotes",
            "description": "Search for quotes. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Search by subject"},
                    "quote_stage": {"type": "string", "description": "Filter by quote stage"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 10)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # SALES ORDER TOOLS (64-69)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_sales_order",
            "description": "Create a new sales order in Zoho CRM. Required: subject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Sales order subject"},
                    "account_name": {"type": "string", "description": "Associated account name"},
                    "status": {"type": "string", "description": "Order status (e.g., 'Created', 'Approved', 'Delivered')"}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_sales_order",
            "description": "Get a sales order by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sales_order_id": {"type": "string", "description": "The Zoho CRM Sales Order ID"}
                },
                "required": ["sales_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_sales_order",
            "description": "Update an existing sales order in Zoho CRM. Required: sales_order_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sales_order_id": {"type": "string", "description": "Sales Order ID to update"},
                    "subject": {"type": "string", "description": "New subject"},
                    "status": {"type": "string", "description": "New status"}
                },
                "required": ["sales_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_sales_order",
            "description": "Delete a sales order from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "sales_order_id": {"type": "string", "description": "Sales Order ID to delete"}
                },
                "required": ["sales_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_sales_orders",
            "description": "Search for sales orders. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Search by subject"},
                    "status": {"type": "string", "description": "Filter by status"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 10)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # PURCHASE ORDER TOOLS (69-74)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_purchase_order",
            "description": "Create a new purchase order in Zoho CRM. Required: subject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Purchase order subject"},
                    "vendor_name": {"type": "string", "description": "Associated vendor name"},
                    "status": {"type": "string", "description": "Order status (e.g., 'Created', 'Approved', 'Delivered')"}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_purchase_order",
            "description": "Get a purchase order by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "purchase_order_id": {"type": "string", "description": "The Zoho CRM Purchase Order ID"}
                },
                "required": ["purchase_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_purchase_order",
            "description": "Update an existing purchase order in Zoho CRM. Required: purchase_order_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "purchase_order_id": {"type": "string", "description": "Purchase Order ID to update"},
                    "subject": {"type": "string", "description": "New subject"},
                    "status": {"type": "string", "description": "New status"}
                },
                "required": ["purchase_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_purchase_order",
            "description": "Delete a purchase order from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "purchase_order_id": {"type": "string", "description": "Purchase Order ID to delete"}
                },
                "required": ["purchase_order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_purchase_orders",
            "description": "Search for purchase orders. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Search by subject"},
                    "status": {"type": "string", "description": "Filter by status"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 10)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # INVOICE TOOLS (74-79)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_invoice",
            "description": "Create a new invoice in Zoho CRM. Required: subject.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Invoice subject"},
                    "account_name": {"type": "string", "description": "Associated account name"},
                    "status": {"type": "string", "description": "Invoice status (e.g., 'Created', 'Approved', 'Paid')"}
                },
                "required": ["subject"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_invoice",
            "description": "Get an invoice by ID from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "The Zoho CRM Invoice ID"}
                },
                "required": ["invoice_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_invoice",
            "description": "Update an existing invoice in Zoho CRM. Required: invoice_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Invoice ID to update"},
                    "subject": {"type": "string", "description": "New subject"},
                    "status": {"type": "string", "description": "New status"}
                },
                "required": ["invoice_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_invoice",
            "description": "Delete an invoice from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {"type": "string", "description": "Invoice ID to delete"}
                },
                "required": ["invoice_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_invoices",
            "description": "Search for invoices. All parameters are optional filters.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subject": {"type": "string", "description": "Search by subject"},
                    "status": {"type": "string", "description": "Filter by status"},
                    "limit": {"type": "integer", "description": "Maximum number of results (default: 10)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # HEALTH CHECK (79)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "zoho_health_check",
            "description": "Check if Zoho CRM API is accessible and healthy.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - FILE MANAGEMENT (80-81)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "upload_file_to_record",
            "description": "Upload a file attachment to a CRM record. Required: module, record_id, file_path.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, Accounts, Deals, etc.)"},
                    "record_id": {"type": "string", "description": "Record ID to attach file to"},
                    "file_path": {"type": "string", "description": "Full path to the file to upload"}
                },
                "required": ["module", "record_id", "file_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_record_attachments",
            "description": "Get list of all file attachments for a record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name"},
                    "record_id": {"type": "string", "description": "Record ID"}
                },
                "required": ["module", "record_id"]
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - EMAIL (82-83)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "send_email_from_crm",
            "description": "Send an email directly from Zoho CRM. Required: to_emails, from_email, subject, content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "to_emails": {"type": "array", "items": {"type": "string"}, "description": "List of recipient email addresses"},
                    "from_email": {"type": "string", "description": "Sender email (must be configured in Zoho CRM)"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "content": {"type": "string", "description": "Email body (HTML supported)"},
                    "cc_emails": {"type": "array", "items": {"type": "string"}, "description": "CC recipients (optional)"}
                },
                "required": ["to_emails", "from_email", "subject", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email_to_record",
            "description": "Send email to a specific CRM record (Lead, Contact, etc.). Required: module, record_id, from_email, subject, content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, etc.)"},
                    "record_id": {"type": "string", "description": "Record ID"},
                    "from_email": {"type": "string", "description": "Sender email"},
                    "subject": {"type": "string", "description": "Email subject"},
                    "content": {"type": "string", "description": "Email body"}
                },
                "required": ["module", "record_id", "from_email", "subject", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_email_templates",
            "description": "List available email templates in Zoho CRM. Optionally filter by module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Filter templates by module (Leads, Contacts, etc.). Optional."}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email_with_template",
            "description": "Send an email to a CRM record using a pre-built email template. Required: module, record_id, template_id, from_email. Use get_email_templates first to find the template ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name (Leads, Contacts, etc.)"},
                    "record_id": {"type": "string", "description": "Record ID to send email to"},
                    "template_id": {"type": "string", "description": "Email template ID (get from get_email_templates)"},
                    "from_email": {"type": "string", "description": "Sender email address (must be configured in Zoho CRM)"}
                },
                "required": ["module", "record_id", "template_id", "from_email"]
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - BULK OPERATIONS (84-86)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "bulk_create_records",
            "description": "Create multiple records at once (up to 100). Required: module, records_json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name"},
                    "records_json": {"type": "string", "description": "JSON string with array of records (e.g., '[{\"Last_Name\":\"Smith\",\"Company\":\"ABC\"}]')"},
                    "trigger_workflow": {"type": "boolean", "description": "Trigger workflow rules (default: false)"}
                },
                "required": ["module", "records_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bulk_update_records",
            "description": "Update multiple records at once (up to 100). Required: module, records_json. Each record must include 'id' field.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name"},
                    "records_json": {"type": "string", "description": "JSON string with array of records (must include 'id' field)"},
                    "trigger_workflow": {"type": "boolean", "description": "Trigger workflow rules (default: false)"}
                },
                "required": ["module", "records_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "bulk_delete_records",
            "description": "Delete multiple records at once (up to 100). Required: module, record_ids.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name"},
                    "record_ids": {"type": "array", "items": {"type": "string"}, "description": "List of record IDs to delete (max 100)"}
                },
                "required": ["module", "record_ids"]
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - CUSTOM MODULES (87-88)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "discover_all_modules",
            "description": "Discover all CRM modules (standard + custom). Use this to find custom module names.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_module_fields",
            "description": "Get all fields for any module (including custom modules).",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"}
                },
                "required": ["module"]
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - WORKFLOWS (89)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_workflow_rules",
            "description": "Get all workflow automation rules. Optionally filter by module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Filter by module name (optional)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - BLUEPRINTS (90)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_blueprint_for_record",
            "description": "Get blueprint process details and available transitions for a record.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name"},
                    "record_id": {"type": "string", "description": "Record ID"}
                },
                "required": ["module", "record_id"]
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - PRICE BOOKS (91-92)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "create_price_book",
            "description": "Create a new price book. Required: pricing_name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pricing_name": {"type": "string", "description": "Price book name"},
                    "description": {"type": "string", "description": "Description (optional)"}
                },
                "required": ["pricing_name"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_all_price_books",
            "description": "Get all price books from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - WEBFORMS (93)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_webforms",
            "description": "Get all web forms. Optionally filter by module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Filter by module (optional)"}
                },
                "required": []
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - TERRITORIES (94-95)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_territories",
            "description": "Get all territories from Zoho CRM.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "assign_territory",
            "description": "Assign a territory to a record. Required: module, record_id, territory_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module name"},
                    "record_id": {"type": "string", "description": "Record ID"},
                    "territory_id": {"type": "string", "description": "Territory ID to assign"}
                },
                "required": ["module", "record_id", "territory_id"]
            }
        }
    },

    # ========================================================================
    # ADVANCED TOOLS - METADATA & CONFIGURATION (96-105)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "get_field_info",
            "description": "Get field metadata for a module or specific field. Required: module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name (Leads, Contacts, etc.)"},
                    "field_id": {"type": "string", "description": "Optional field ID to get specific field details"},
                    "field_type": {"type": "string", "description": "'all' (default) or 'unused' to show only unused fields"}
                },
                "required": ["module"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_field_settings",
            "description": "Update custom field settings. Max 5 fields per call. Cannot update system-defined fields or change data type. Required: module, field_id, updates_json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"},
                    "field_id": {"type": "string", "description": "Field ID to update"},
                    "updates_json": {"type": "string", "description": "JSON string with updates (e.g., '{\"field_label\": \"New Label\"}')"}
                },
                "required": ["module", "field_id", "updates_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "remove_custom_field",
            "description": "Delete a custom field from a module. Only custom fields can be deleted. Cannot delete fields used in workflows/rules. Required: module, field_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"},
                    "field_id": {"type": "string", "description": "Field ID to delete"}
                },
                "required": ["module", "field_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_module_layouts",
            "description": "Get all layouts for a module. Supported: Leads, Accounts, Contacts, Deals, Campaigns, Tasks, Cases, Events, Calls, Solutions, Products, Vendors, Price Books, Quotes, Sales Orders, Purchase Orders, Invoices, Appointments, Services, Custom.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"}
                },
                "required": ["module"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_layout_details",
            "description": "Get specific layout configuration for a module. Required: module, layout_id.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"},
                    "layout_id": {"type": "string", "description": "Layout ID"}
                },
                "required": ["module", "layout_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "update_layout_configuration",
            "description": "Update a custom layout configuration. Max 5 field actions and 5 sections per call. Required: module, layout_id, updates_json.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"},
                    "layout_id": {"type": "string", "description": "Layout ID to update"},
                    "updates_json": {"type": "string", "description": "JSON string with layout updates"}
                },
                "required": ["module", "layout_id", "updates_json"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_layout",
            "description": "Delete a custom layout and transfer records to another layout. transfer_to is REQUIRED. Required: module, layout_id, transfer_to.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"},
                    "layout_id": {"type": "string", "description": "Layout ID to delete"},
                    "transfer_to": {"type": "string", "description": "Layout ID to transfer existing records to (required)"}
                },
                "required": ["module", "layout_id", "transfer_to"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_inventory_templates",
            "description": "Get inventory templates for Quotes, Invoices, Sales Orders, Purchase Orders. Optionally filter by module or category.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Optional module filter (Quotes, Invoices, Purchase_Orders, Sales_Orders)"},
                    "category": {"type": "string", "description": "Optional category filter: 'favorite', 'created_by_me', 'shared_with_me', 'draft'"}
                },
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_template_details",
            "description": "Get a specific inventory template by ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "template_id": {"type": "string", "description": "Template ID"}
                },
                "required": ["template_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_module_tags",
            "description": "Get all tags for a module. Required: module.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name (mandatory)"},
                    "my_tags_only": {"type": "boolean", "description": "If true, only return tags created by current user (default: false)"}
                },
                "required": ["module"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_tags",
            "description": "Find tags by name for a specific module. Required: module, tag_name_contains.",
            "parameters": {
                "type": "object",
                "properties": {
                    "module": {"type": "string", "description": "Module API name"},
                    "tag_name_contains": {"type": "string", "description": "Search term to find in tag names"}
                },
                "required": ["module", "tag_name_contains"]
            }
        }
    },

    # ========================================================================
    # LARGE RESULT SET TOOLS (106-107)
    # ========================================================================
    {
        "type": "function",
        "function": {
            "name": "browse_result_page",
            "description": "Browse a page of results from a large cached result set. Use when a search returned more than 50 records and the user wants to browse them in groups of 20. The result_set_id comes from the [LARGE_RESULT_SET:id] marker in the search response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result_set_id": {"type": "string", "description": "The result set ID from the [LARGE_RESULT_SET:id] marker"},
                    "page": {"type": "integer", "description": "Page number to view (starts at 1). Each page shows 20 records."}
                },
                "required": ["result_set_id", "page"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "export_results_pdf",
            "description": "Export a large cached result set as a PDF report file. Use when a search returned more than 50 records and the user wants a PDF download. The result_set_id comes from the [LARGE_RESULT_SET:id] marker in the search response.",
            "parameters": {
                "type": "object",
                "properties": {
                    "result_set_id": {"type": "string", "description": "The result set ID from the [LARGE_RESULT_SET:id] marker"},
                    "title": {"type": "string", "description": "Optional custom title for the PDF report"}
                },
                "required": ["result_set_id"]
            }
        }
    },
]
