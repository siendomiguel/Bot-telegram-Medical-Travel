"""
Tool Service - Bridge layer mapping 109 tool names to direct zoho_client function calls.
Replaces the MCP server layer for Telegram bot integration.
Includes large result set handling with pagination and PDF export.
"""

import sys
import os
import json
import logging
import asyncio
import uuid
import time
from typing import Optional, List, Dict, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from zoho_client.modules import ZohoModules
from zoho_client.activities import ZohoActivities
from zoho_client.notes import ZohoNotes
from zoho_client.search import ZohoSearch
from zoho_client.files import ZohoFiles
from zoho_client.emails import ZohoEmails
from zoho_client.bulk_operations import ZohoBulkOperations
from zoho_client.custom_modules import ZohoCustomModules
from zoho_client.workflows import ZohoWorkflows
from zoho_client.blueprints import ZohoBlueprints
from zoho_client.pricebooks import ZohoPriceBooks
from zoho_client.webforms import ZohoWebForms
from zoho_client.territories import ZohoTerritories
from zoho_client.metadata import ZohoMetadata
from zoho_client.advanced_operations import ZohoAdvancedOperations
from zoho_client.coql import ZohoCOQL

logger = logging.getLogger(__name__)


class ToolService:
    """Bridge layer that maps 107 tool names to direct zoho_client function calls."""

    LARGE_RESULT_THRESHOLD = 50
    CACHE_TTL_SECONDS = 600  # 10 minutes
    PAGE_SIZE = 20

    def __init__(self):
        """Initialize all zoho_client instances."""
        # In-memory result cache for large result sets (10-min TTL)
        self._result_cache: Dict[str, Dict[str, Any]] = {}
        self.modules_client = ZohoModules()
        self.activities_client = ZohoActivities()
        self.notes_client = ZohoNotes()
        self.search_client = ZohoSearch()
        self.files_client = ZohoFiles()
        self.emails_client = ZohoEmails()
        self.bulk_client = ZohoBulkOperations()
        self.custom_modules_client = ZohoCustomModules()
        self.workflows_client = ZohoWorkflows()
        self.blueprints_client = ZohoBlueprints()
        self.pricebooks_client = ZohoPriceBooks()
        self.webforms_client = ZohoWebForms()
        self.territories_client = ZohoTerritories()
        self.metadata_client = ZohoMetadata()
        self.advanced_ops_client = ZohoAdvancedOperations()
        self.coql_client = ZohoCOQL()

        # Build tool dispatch map
        self._tool_map: Dict[str, Any] = {
            # Lead tools
            "create_lead": self._create_lead,
            "get_lead": self._get_lead,
            "update_lead": self._update_lead,
            "delete_lead": self._delete_lead,
            "convert_lead_to_contact": self._convert_lead_to_contact,
            # Search tools
            "search_leads": self._search_leads,
            "count_all_records": self._count_all_records,
            "search_by_email": self._search_by_email,
            "search_by_phone": self._search_by_phone,
            "search_by_word": self._search_by_word,
            # Contact tools
            "create_contact": self._create_contact,
            "get_contact": self._get_contact,
            "update_contact": self._update_contact,
            "delete_contact": self._delete_contact,
            "search_contacts": self._search_contacts,
            # Account tools
            "create_account": self._create_account,
            "get_account": self._get_account,
            "update_account": self._update_account,
            "delete_account": self._delete_account,
            "search_accounts": self._search_accounts,
            # Deal tools
            "create_deal": self._create_deal,
            "get_deal": self._get_deal,
            "update_deal": self._update_deal,
            "delete_deal": self._delete_deal,
            "search_deals": self._search_deals,
            # Product tools
            "create_product": self._create_product,
            "get_product": self._get_product,
            "update_product": self._update_product,
            "delete_product": self._delete_product,
            "search_products": self._search_products,
            # Task tools
            "create_task": self._create_task,
            "get_task": self._get_task,
            "get_tasks_for_record": self._get_tasks_for_record,
            "get_pending_tasks": self._get_pending_tasks,
            "check_multiple_leads_for_tasks": self._check_multiple_leads_for_tasks,
            "search_tasks": self._search_tasks,
            "update_task": self._update_task,
            "delete_task": self._delete_task,
            # Event tools
            "create_event": self._create_event,
            "get_event": self._get_event,
            "get_events_for_record": self._get_events_for_record,
            "update_event": self._update_event,
            "delete_event": self._delete_event,
            # Call tools
            "create_call": self._create_call,
            "get_call": self._get_call,
            "update_call": self._update_call,
            "delete_call": self._delete_call,
            "get_calls_for_record": self._get_calls_for_record,
            # Note tools
            "create_note": self._create_note,
            "get_notes_for_record": self._get_notes_for_record,
            "update_note": self._update_note,
            "delete_note": self._delete_note,
            # Vendor tools
            "create_vendor": self._create_vendor,
            "get_vendor": self._get_vendor,
            "update_vendor": self._update_vendor,
            "delete_vendor": self._delete_vendor,
            "search_vendors": self._search_vendors,
            # Quote tools
            "create_quote": self._create_quote,
            "get_quote": self._get_quote,
            "update_quote": self._update_quote,
            "delete_quote": self._delete_quote,
            "search_quotes": self._search_quotes,
            # Sales Order tools
            "create_sales_order": self._create_sales_order,
            "get_sales_order": self._get_sales_order,
            "update_sales_order": self._update_sales_order,
            "delete_sales_order": self._delete_sales_order,
            "search_sales_orders": self._search_sales_orders,
            # Purchase Order tools
            "create_purchase_order": self._create_purchase_order,
            "get_purchase_order": self._get_purchase_order,
            "update_purchase_order": self._update_purchase_order,
            "delete_purchase_order": self._delete_purchase_order,
            "search_purchase_orders": self._search_purchase_orders,
            # Invoice tools
            "create_invoice": self._create_invoice,
            "get_invoice": self._get_invoice,
            "update_invoice": self._update_invoice,
            "delete_invoice": self._delete_invoice,
            "search_invoices": self._search_invoices,
            # Health check
            "zoho_health_check": self._zoho_health_check,
            # Advanced: File tools
            "upload_file_to_record": self._upload_file_to_record,
            "get_record_attachments": self._get_record_attachments,
            # Advanced: Email tools
            "send_email_from_crm": self._send_email_from_crm,
            "send_email_to_record": self._send_email_to_record,
            "get_email_templates": self._get_email_templates,
            "send_email_with_template": self._send_email_with_template,
            # Advanced: Bulk operations
            "bulk_create_records": self._bulk_create_records,
            "bulk_update_records": self._bulk_update_records,
            "bulk_delete_records": self._bulk_delete_records,
            # Advanced: Custom modules
            "discover_all_modules": self._discover_all_modules,
            "get_module_fields": self._get_module_fields,
            # Advanced: Workflows
            "get_workflow_rules": self._get_workflow_rules,
            # Advanced: Blueprints
            "get_blueprint_for_record": self._get_blueprint_for_record,
            # Advanced: Price books
            "create_price_book": self._create_price_book,
            "get_all_price_books": self._get_all_price_books,
            # Advanced: Webforms
            "get_webforms": self._get_webforms,
            # Advanced: Territories
            "get_territories": self._get_territories,
            "assign_territory": self._assign_territory,
            # Advanced: Metadata
            "get_field_info": self._get_field_info,
            "update_field_settings": self._update_field_settings,
            "remove_custom_field": self._remove_custom_field,
            "get_module_layouts": self._get_module_layouts,
            "get_layout_details": self._get_layout_details,
            "update_layout_configuration": self._update_layout_configuration,
            "delete_layout": self._delete_layout,
            "list_inventory_templates": self._list_inventory_templates,
            "get_template_details": self._get_template_details,
            "list_module_tags": self._list_module_tags,
            "search_tags": self._search_tags,
            # Large result set tools
            "browse_result_page": self._browse_result_page,
            "export_results_pdf": self._export_results_pdf,
        }

    async def execute_tool(self, tool_name: str, arguments: dict) -> str:
        """Dispatch to the right handler based on tool_name."""
        handler = self._tool_map.get(tool_name)
        if not handler:
            return f"Unknown tool: {tool_name}"
        try:
            return await handler(arguments)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}: {e}")
            return f"Error executing {tool_name}: {str(e)}"

    # ========================================================================
    # LARGE RESULT SET HELPERS
    # ========================================================================

    def _cleanup_expired_cache(self) -> None:
        """Remove expired entries from the result cache."""
        now = time.time()
        expired = [k for k, v in self._result_cache.items()
                   if now - v["timestamp"] > self.CACHE_TTL_SECONDS]
        for k in expired:
            del self._result_cache[k]

    def _record_one_liner(self, record: Dict[str, Any], module: str) -> str:
        """Format a single record as a one-line summary."""
        rec_id = record.get("id", "?")

        if module == "Leads":
            name = f"{record.get('First_Name', '')} {record.get('Last_Name', '')}".strip() or "N/A"
            return f"{name} - {record.get('Company', 'N/A')} ({record.get('Lead_Status', 'N/A')}) [ID: {rec_id}]"

        if module == "Contacts":
            name = f"{record.get('First_Name', '')} {record.get('Last_Name', '')}".strip() or "N/A"
            return f"{name} - {record.get('Email', 'N/A')} [ID: {rec_id}]"

        if module == "Accounts":
            return f"{record.get('Account_Name', 'N/A')} - {record.get('Industry', 'N/A')} [ID: {rec_id}]"

        if module == "Deals":
            amount = record.get('Amount')
            amt_str = f"${float(amount):,.2f}" if amount else "N/A"
            return f"{record.get('Deal_Name', 'N/A')} - {record.get('Stage', 'N/A')} ({amt_str}) [ID: {rec_id}]"

        if module == "Products":
            price = record.get('Unit_Price')
            price_str = f"${float(price):,.2f}" if price else "N/A"
            return f"{record.get('Product_Name', 'N/A')} - {price_str} [ID: {rec_id}]"

        if module == "Tasks":
            return f"{record.get('Subject', 'N/A')} - {record.get('Status', 'N/A')} (Due: {record.get('Due_Date', 'N/A')}) [ID: {rec_id}]"

        if module == "Vendors":
            return f"{record.get('Vendor_Name', 'N/A')} - {record.get('Email', 'N/A')} [ID: {rec_id}]"

        # Generic fallback for Quotes, Sales_Orders, Purchase_Orders, Invoices
        name = record.get('Subject') or record.get('Name') or 'N/A'
        status = record.get('Status') or record.get('Quote_Stage') or 'N/A'
        return f"{name} - {status} [ID: {rec_id}]"

    def _cache_and_summarize(self, records: List[Dict[str, Any]], module: str) -> str:
        """Cache a large result set and return a summary for the LLM."""
        self._cleanup_expired_cache()

        result_set_id = str(uuid.uuid4())[:8]
        self._result_cache[result_set_id] = {
            "records": records,
            "module": module,
            "timestamp": time.time(),
        }

        total = len(records)
        total_pages = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE

        # Preview first 5 records
        preview_lines = []
        for i, record in enumerate(records[:5], 1):
            preview_lines.append(f"  {i}. {self._record_one_liner(record, module)}")
        preview = "\n".join(preview_lines)

        return (
            f"Found {total} {module.lower()} (showing first 5 of {total}):\n\n"
            f"{preview}\n\n"
            f"... and {total - 5} more records.\n\n"
            f"[LARGE_RESULT_SET:{result_set_id}]\n\n"
            f"This result set has {total_pages} pages of {self.PAGE_SIZE} records each.\n"
            f"Ask the user: would they like to browse in groups of {self.PAGE_SIZE}, "
            f"or get a PDF report of all {total} records?\n"
            f"- To browse: call browse_result_page with result_set_id=\"{result_set_id}\" and page=1\n"
            f"- To export PDF: call export_results_pdf with result_set_id=\"{result_set_id}\""
        )

    async def _browse_result_page(self, args: dict) -> str:
        """Return a page of records from a cached large result set."""
        try:
            result_set_id = args["result_set_id"]
            page = args.get("page", 1)

            self._cleanup_expired_cache()

            if result_set_id not in self._result_cache:
                return ("Result set expired or not found (cache clears on restart and after 10 minutes). "
                        "You MUST re-run the original search to generate a new result set, then use the new result_set_id. "
                        "Tell the user: the previous results expired and you're re-running the search now.")

            cache_entry = self._result_cache[result_set_id]
            records = cache_entry["records"]
            module = cache_entry["module"]
            total = len(records)
            total_pages = (total + self.PAGE_SIZE - 1) // self.PAGE_SIZE

            if page < 1 or page > total_pages:
                return f"Invalid page {page}. Valid range: 1-{total_pages}"

            start = (page - 1) * self.PAGE_SIZE
            end = min(start + self.PAGE_SIZE, total)
            page_records = records[start:end]

            output = f"Page {page}/{total_pages} ({total} total {module.lower()}):\n\n"
            for i, record in enumerate(page_records, start + 1):
                output += f"{i}. {self._record_one_liner(record, module)}\n"

            output += f"\nShowing {start + 1}-{end} of {total}."
            if page < total_pages:
                output += f" Next page: browse_result_page with result_set_id=\"{result_set_id}\", page={page + 1}"

            return output

        except Exception as e:
            logger.error(f"Error browsing result page: {e}")
            return f"Error: {str(e)}"

    async def _export_results_pdf(self, args: dict) -> str:
        """Generate a PDF from a cached large result set."""
        try:
            result_set_id = args["result_set_id"]
            title = args.get("title")

            self._cleanup_expired_cache()

            if result_set_id not in self._result_cache:
                return ("Result set expired or not found (cache clears on restart and after 10 minutes). "
                        "You MUST re-run the original search to generate a new result set, then use the new result_set_id. "
                        "Tell the user: the previous results expired and you're re-running the search now.")

            cache_entry = self._result_cache[result_set_id]
            records = cache_entry["records"]
            module = cache_entry["module"]

            if not title:
                title = f"{module} Report - {len(records)} records"

            from utils.pdf_export import generate_crm_pdf
            filepath = generate_crm_pdf(records, module, title)

            return f"PDF report generated with {len(records)} {module.lower()}.\n[SEND_FILE:{filepath}]"

        except Exception as e:
            logger.error(f"Error exporting PDF: {e}")
            return f"Error generating PDF: {str(e)}"

    # ========================================================================
    # LEAD TOOLS
    # ========================================================================

    async def _create_lead(self, args: dict) -> str:
        try:
            last_name = args["last_name"]
            company = args["company"]
            first_name = args.get("first_name")
            email = args.get("email")
            phone = args.get("phone")
            lead_source = args.get("lead_source")
            lead_status = args.get("lead_status")
            industry = args.get("industry")

            data = {
                "Last_Name": last_name,
                "Company": company
            }
            if first_name:
                data["First_Name"] = first_name
            if email:
                data["Email"] = email
            if phone:
                data["Phone"] = phone
            if lead_source:
                data["Lead_Source"] = lead_source
            if lead_status:
                data["Lead_Status"] = lead_status
            if industry:
                data["Industry"] = industry

            result = await self.modules_client.create_record("Leads", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    lead_id = record["details"]["id"]
                    return f"Lead created successfully!\nLead ID: {lead_id}\nName: {first_name or ''} {last_name}\nCompany: {company}"

            return f"Failed to create lead: {result}"

        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return f"Error creating lead: {str(e)}"

    async def _get_lead(self, args: dict) -> str:
        try:
            lead_id = args["lead_id"]
            result = await self.modules_client.get_record(
                "Leads",
                lead_id,
                fields=["First_Name", "Last_Name", "Email", "Phone", "Company", "Lead_Status", "Lead_Source", "Created_Time", "Modified_Time"]
            )

            if result.get("data") and len(result["data"]) > 0:
                lead = result["data"][0]
                output = "Lead Details:\n\n"
                output += f"Name: {lead.get('Full_Name', 'N/A')}\n"
                output += f"Email: {lead.get('Email', 'N/A')}\n"
                output += f"Phone: {lead.get('Phone', 'N/A')}\n"
                output += f"Company: {lead.get('Company', 'N/A')}\n"
                output += f"Status: {lead.get('Lead_Status', 'N/A')}\n"
                output += f"Source: {lead.get('Lead_Source', 'N/A')}\n"
                output += f"Created: {lead.get('Created_Time', 'N/A')}\n"
                output += f"Modified: {lead.get('Modified_Time', 'N/A')}\n"
                output += f"ID: {lead['id']}"
                return output

            return "Lead not found"

        except Exception as e:
            logger.error(f"Error getting lead: {e}")
            return f"Error: {str(e)}"

    async def _update_lead(self, args: dict) -> str:
        try:
            lead_id = args["lead_id"]
            first_name = args.get("first_name")
            last_name = args.get("last_name")
            email = args.get("email")
            phone = args.get("phone")
            company = args.get("company")
            lead_status = args.get("lead_status")
            lead_source = args.get("lead_source")

            data = {}
            if first_name:
                data["First_Name"] = first_name
            if last_name:
                data["Last_Name"] = last_name
            if email:
                data["Email"] = email
            if phone:
                data["Phone"] = phone
            if company:
                data["Company"] = company
            if lead_status:
                data["Lead_Status"] = lead_status
            if lead_source:
                data["Lead_Source"] = lead_source

            if not data:
                return "No fields provided to update"

            result = await self.modules_client.update_record("Leads", lead_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Lead updated successfully!\nLead ID: {lead_id}"

            return f"Failed to update lead: {result}"

        except Exception as e:
            logger.error(f"Error updating lead: {e}")
            return f"Error: {str(e)}"

    async def _delete_lead(self, args: dict) -> str:
        try:
            lead_id = args["lead_id"]
            result = await self.modules_client.delete_record("Leads", lead_id)
            return f"Lead deleted successfully! ID: {lead_id}"
        except Exception as e:
            logger.error(f"Error deleting lead: {e}")
            return f"Error: {str(e)}"

    async def _convert_lead_to_contact(self, args: dict) -> str:
        try:
            lead_id = args["lead_id"]
            create_account = args.get("create_account", True)
            create_deal = args.get("create_deal", False)

            convert_to = {
                "Contacts": True,
                "Accounts": create_account,
                "Deals": create_deal
            }

            result = await self.modules_client.convert_lead(lead_id, convert_to)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    output = "Lead converted successfully!\n\n"
                    details = record.get("details", {})

                    if "Contacts" in details:
                        output += f"Contact ID: {details['Contacts']}\n"
                    if "Accounts" in details:
                        output += f"Account ID: {details['Accounts']}\n"
                    if "Deals" in details:
                        output += f"Deal ID: {details['Deals']}\n"

                    return output

            return f"Failed to convert lead: {result}"

        except Exception as e:
            logger.error(f"Error converting lead: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # SEARCH TOOLS
    # ========================================================================

    async def _search_leads(self, args: dict) -> str:
        try:
            last_name = args.get("last_name")
            email = args.get("email")
            phone = args.get("phone")
            company = args.get("company")
            lead_status = args.get("lead_status")
            created_after = args.get("created_after")

            conditions = {}
            if last_name:
                conditions["Last_Name__contains"] = last_name
            if email:
                conditions["Email__contains"] = email
            if phone:
                conditions["Phone"] = phone
            if company:
                conditions["Company__contains"] = company
            if lead_status:
                conditions["Lead_Status"] = lead_status
            if created_after:
                conditions["Created_Time__greater_than"] = created_after

            search_fields = ["First_Name", "Last_Name", "Email", "Phone", "Company", "Lead_Status", "Lead_Source", "Created_Time"]

            if not conditions:
                result = await self.modules_client.get_records("Leads", page=1, per_page=200)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Leads",
                    conditions=conditions,
                    fields=search_fields
                )

            if result.get("data") and len(result["data"]) > 0:
                leads = result["data"]

                if len(leads) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(leads, "Leads")

                output = f"Found {len(leads)} lead(s):\n\n"
                for lead in leads:
                    name = f"{lead.get('First_Name', '')} {lead.get('Last_Name', '')}".strip() or "N/A"
                    output += f"- {name}\n"
                    output += f"  Company: {lead.get('Company', 'N/A')}\n"
                    output += f"  Email: {lead.get('Email', 'N/A')}\n"
                    output += f"  Phone: {lead.get('Phone', 'N/A')}\n"
                    output += f"  Status: {lead.get('Lead_Status', 'N/A')}\n"
                    output += f"  Source: {lead.get('Lead_Source', 'N/A')}\n"
                    output += f"  Created: {lead.get('Created_Time', 'N/A')}\n"
                    output += f"  ID: {lead['id']}\n\n"
                return output

            return "No leads found matching your criteria"

        except Exception as e:
            logger.error(f"Error searching leads: {e}")
            return f"Error: {str(e)}"

    async def _count_all_records(self, args: dict) -> str:
        try:
            module = args["module"]
            logger.info(f"Counting all records in {module}...")

            all_records = await self.modules_client.get_all_records(
                module=module,
                fields=["id"]
            )

            total_count = len(all_records)
            return f"Total: {total_count:,} {module.lower()} in your CRM"

        except Exception as e:
            logger.error(f"Error counting {args.get('module', 'unknown')}: {e}")
            return f"Error counting {args.get('module', 'unknown')}: {str(e)}"

    async def _search_by_email(self, args: dict) -> str:
        try:
            module = args["module"]
            email = args["email"]
            result = await self.search_client.search_by_email(module, email)

            if result.get("data") and len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(result["data"], module)

            formatted = self.search_client.format_search_results(result, module)
            return formatted
        except Exception as e:
            logger.error(f"Error searching by email: {e}")
            return f"Error: {str(e)}"

    async def _search_by_phone(self, args: dict) -> str:
        try:
            module = args["module"]
            phone = args["phone"]
            result = await self.search_client.search_by_phone(module, phone)

            if result.get("data") and len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(result["data"], module)

            formatted = self.search_client.format_search_results(result, module)
            return formatted
        except Exception as e:
            logger.error(f"Error searching by phone: {e}")
            return f"Error: {str(e)}"

    async def _search_by_word(self, args: dict) -> str:
        try:
            module = args["module"]
            word = args["word"]
            limit = args.get("limit", 20)

            result = await self.search_client.search_by_word(module, word, page=1, per_page=limit)

            if result.get("data") and len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(result["data"], module)

            if result.get("data") and len(result["data"]) > 0:
                output = f"Found {len(result['data'])} record(s) matching '{word}':\n\n"
                for record in result["data"]:
                    if module == "Leads":
                        output += f"- {record.get('First_Name', '')} {record.get('Last_Name', 'N/A')} - {record.get('Company', 'N/A')}\n"
                        output += f"  Email: {record.get('Email', 'N/A')}\n"
                        output += f"  Status: {record.get('Lead_Status', 'N/A')}\n"
                    elif module == "Contacts":
                        output += f"- {record.get('First_Name', '')} {record.get('Last_Name', 'N/A')}\n"
                        output += f"  Email: {record.get('Email', 'N/A')}\n"
                    elif module == "Accounts":
                        output += f"- {record.get('Account_Name', 'N/A')}\n"
                        output += f"  Website: {record.get('Website', 'N/A')}\n"
                    elif module == "Deals":
                        output += f"- {record.get('Deal_Name', 'N/A')}\n"
                        output += f"  Amount: ${record.get('Amount', 0):,.2f}\n"
                    else:
                        name_field = record.get('Subject') or record.get('Name') or record.get('Product_Name') or 'Unknown'
                        output += f"- {name_field}\n"

                    output += f"  Created: {record.get('Created_Time', 'N/A')}\n"
                    output += f"  ID: {record['id']}\n\n"

                return output

            return f"No records found matching '{word}'"

        except Exception as e:
            logger.error(f"Error searching by word: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # CONTACT TOOLS
    # ========================================================================

    async def _create_contact(self, args: dict) -> str:
        try:
            last_name = args["last_name"]
            first_name = args.get("first_name")
            email = args.get("email")
            phone = args.get("phone")
            account_name = args.get("account_name")

            data = {"Last_Name": last_name}
            if first_name:
                data["First_Name"] = first_name
            if email:
                data["Email"] = email
            if phone:
                data["Phone"] = phone
            if account_name:
                data["Account_Name"] = account_name

            result = await self.modules_client.create_record("Contacts", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    contact_id = record["details"]["id"]
                    return f"Contact created successfully!\nContact ID: {contact_id}"

            return f"Failed to create contact: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_contact(self, args: dict) -> str:
        try:
            contact_id = args["contact_id"]
            result = await self.modules_client.get_record(
                "Contacts",
                contact_id,
                fields=["First_Name", "Last_Name", "Email", "Phone", "Account_Name", "Created_Time", "Modified_Time"]
            )

            if result.get("data") and len(result["data"]) > 0:
                contact = result["data"][0]
                output = "Contact Details:\n\n"
                output += f"Name: {contact.get('Full_Name', 'N/A')}\n"
                output += f"Email: {contact.get('Email', 'N/A')}\n"
                output += f"Phone: {contact.get('Phone', 'N/A')}\n"
                output += f"Account: {contact.get('Account_Name', {}).get('name', 'N/A') if isinstance(contact.get('Account_Name'), dict) else 'N/A'}\n"
                output += f"Created: {contact.get('Created_Time', 'N/A')}\n"
                output += f"Modified: {contact.get('Modified_Time', 'N/A')}\n"
                output += f"ID: {contact['id']}"
                return output

            return "Contact not found"

        except Exception as e:
            logger.error(f"Error getting contact: {e}")
            return f"Error: {str(e)}"

    async def _update_contact(self, args: dict) -> str:
        try:
            contact_id = args["contact_id"]
            first_name = args.get("first_name")
            last_name = args.get("last_name")
            email = args.get("email")
            phone = args.get("phone")
            account_name = args.get("account_name")

            data = {}
            if first_name:
                data["First_Name"] = first_name
            if last_name:
                data["Last_Name"] = last_name
            if email:
                data["Email"] = email
            if phone:
                data["Phone"] = phone
            if account_name:
                data["Account_Name"] = account_name

            if not data:
                return "No fields provided to update"

            result = await self.modules_client.update_record("Contacts", contact_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Contact updated successfully!\nContact ID: {contact_id}"

            return f"Failed to update contact: {result}"

        except Exception as e:
            logger.error(f"Error updating contact: {e}")
            return f"Error: {str(e)}"

    async def _delete_contact(self, args: dict) -> str:
        try:
            contact_id = args["contact_id"]
            result = await self.modules_client.delete_record("Contacts", contact_id)
            return f"Contact deleted successfully! ID: {contact_id}"
        except Exception as e:
            logger.error(f"Error deleting contact: {e}")
            return f"Error: {str(e)}"

    async def _search_contacts(self, args: dict) -> str:
        try:
            last_name = args.get("last_name")
            email = args.get("email")
            phone = args.get("phone")
            account_name = args.get("account_name")

            conditions = {}
            if last_name:
                conditions["Last_Name__contains"] = last_name
            if email:
                conditions["Email__contains"] = email
            if phone:
                conditions["Phone"] = phone
            if account_name:
                conditions["Account_Name__contains"] = account_name

            search_fields = ["First_Name", "Last_Name", "Email", "Phone", "Account_Name", "Created_Time"]

            if not conditions:
                result = await self.modules_client.get_records("Contacts", page=1, per_page=200)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Contacts",
                    conditions=conditions,
                    fields=search_fields
                )

            if result.get("data") and len(result["data"]) > 0:
                contacts = result["data"]

                if len(contacts) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(contacts, "Contacts")

                output = f"Found {len(contacts)} contact(s):\n\n"
                for contact in contacts:
                    name = f"{contact.get('First_Name', '')} {contact.get('Last_Name', '')}".strip() or "N/A"
                    acct = contact.get('Account_Name', {}).get('name', 'N/A') if isinstance(contact.get('Account_Name'), dict) else 'N/A'
                    output += f"- {name}\n"
                    output += f"  Email: {contact.get('Email', 'N/A')}\n"
                    output += f"  Phone: {contact.get('Phone', 'N/A')}\n"
                    output += f"  Account: {acct}\n"
                    output += f"  Created: {contact.get('Created_Time', 'N/A')}\n"
                    output += f"  ID: {contact['id']}\n\n"
                return output

            return "No contacts found matching your criteria"

        except Exception as e:
            logger.error(f"Error searching contacts: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # ACCOUNT TOOLS
    # ========================================================================

    async def _create_account(self, args: dict) -> str:
        try:
            account_name = args["account_name"]
            phone = args.get("phone")
            website = args.get("website")
            industry = args.get("industry")

            data = {"Account_Name": account_name}
            if phone:
                data["Phone"] = phone
            if website:
                data["Website"] = website
            if industry:
                data["Industry"] = industry

            result = await self.modules_client.create_record("Accounts", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    account_id = record["details"]["id"]
                    return f"Account created successfully!\nAccount ID: {account_id}"

            return f"Failed to create account: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_account(self, args: dict) -> str:
        try:
            account_id = args["account_id"]
            result = await self.modules_client.get_record(
                "Accounts",
                account_id,
                fields=["Account_Name", "Phone", "Website", "Industry", "Annual_Revenue"]
            )

            if result.get("data") and len(result["data"]) > 0:
                account = result["data"][0]
                output = "Account Details:\n\n"
                output += f"Name: {account.get('Account_Name', 'N/A')}\n"
                output += f"Phone: {account.get('Phone', 'N/A')}\n"
                output += f"Website: {account.get('Website', 'N/A')}\n"
                output += f"Industry: {account.get('Industry', 'N/A')}\n"
                output += f"ID: {account['id']}"
                return output

            return "Account not found"

        except Exception as e:
            logger.error(f"Error getting account: {e}")
            return f"Error: {str(e)}"

    async def _update_account(self, args: dict) -> str:
        try:
            account_id = args["account_id"]
            account_name = args.get("account_name")
            phone = args.get("phone")
            website = args.get("website")
            industry = args.get("industry")

            data = {}
            if account_name:
                data["Account_Name"] = account_name
            if phone:
                data["Phone"] = phone
            if website:
                data["Website"] = website
            if industry:
                data["Industry"] = industry

            if not data:
                return "No fields provided to update"

            result = await self.modules_client.update_record("Accounts", account_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Account updated successfully!\nAccount ID: {account_id}"

            return f"Failed to update account: {result}"

        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return f"Error: {str(e)}"

    async def _delete_account(self, args: dict) -> str:
        try:
            account_id = args["account_id"]
            result = await self.modules_client.delete_record("Accounts", account_id)
            return f"Account deleted successfully! ID: {account_id}"
        except Exception as e:
            logger.error(f"Error deleting account: {e}")
            return f"Error: {str(e)}"

    async def _search_accounts(self, args: dict) -> str:
        try:
            account_name = args.get("account_name")
            phone = args.get("phone")
            website = args.get("website")
            industry = args.get("industry")

            conditions = {}
            if account_name:
                conditions["Account_Name__contains"] = account_name
            if phone:
                conditions["Phone"] = phone
            if website:
                conditions["Website__contains"] = website
            if industry:
                conditions["Industry"] = industry

            if not conditions:
                result = await self.modules_client.get_records("Accounts", page=1, per_page=200)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Accounts",
                    conditions=conditions,
                    fields=["Account_Name", "Phone", "Website", "Industry"]
                )

            if result.get("data") and len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(result["data"], "Accounts")

            formatted = self.search_client.format_search_results(result, "Accounts")
            return formatted

        except Exception as e:
            logger.error(f"Error searching accounts: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # DEAL TOOLS
    # ========================================================================

    async def _create_deal(self, args: dict) -> str:
        try:
            deal_name = args["deal_name"]
            stage = args["stage"]
            amount = args.get("amount")
            closing_date = args.get("closing_date")
            account_name = args.get("account_name")
            contact_id = args.get("contact_id")

            data = {
                "Deal_Name": deal_name,
                "Stage": stage
            }
            if amount:
                data["Amount"] = amount
            if closing_date:
                data["Closing_Date"] = closing_date
            if account_name:
                data["Account_Name"] = account_name
            if contact_id:
                data["Contact_Name"] = {"id": contact_id}

            result = await self.modules_client.create_record("Deals", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    deal_id = record["details"]["id"]
                    return f"Deal created successfully!\nDeal ID: {deal_id}"

            return f"Failed to create deal: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_deal(self, args: dict) -> str:
        try:
            deal_id = args["deal_id"]
            result = await self.modules_client.get_record(
                "Deals",
                deal_id,
                fields=["Deal_Name", "Stage", "Amount", "Closing_Date", "Account_Name", "Contact_Name"]
            )

            if result.get("data") and len(result["data"]) > 0:
                deal = result["data"][0]
                output = "Deal Details:\n\n"
                output += f"Name: {deal.get('Deal_Name', 'N/A')}\n"
                output += f"Stage: {deal.get('Stage', 'N/A')}\n"
                output += f"Amount: ${deal.get('Amount', 0):,.2f}\n"
                output += f"Closing Date: {deal.get('Closing_Date', 'N/A')}\n"
                output += f"Account: {deal.get('Account_Name', {}).get('name', 'N/A') if isinstance(deal.get('Account_Name'), dict) else 'N/A'}\n"
                output += f"ID: {deal['id']}"
                return output

            return "Deal not found"

        except Exception as e:
            logger.error(f"Error getting deal: {e}")
            return f"Error: {str(e)}"

    async def _update_deal(self, args: dict) -> str:
        try:
            deal_id = args["deal_id"]
            deal_name = args.get("deal_name")
            stage = args.get("stage")
            amount = args.get("amount")
            closing_date = args.get("closing_date")
            account_name = args.get("account_name")
            contact_id = args.get("contact_id")

            data = {}
            if deal_name:
                data["Deal_Name"] = deal_name
            if stage:
                data["Stage"] = stage
            if amount is not None:
                data["Amount"] = amount
            if closing_date:
                data["Closing_Date"] = closing_date
            if account_name:
                data["Account_Name"] = account_name
            if contact_id:
                data["Contact_Name"] = {"id": contact_id}

            if not data:
                return "No fields provided to update"

            result = await self.modules_client.update_record("Deals", deal_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Deal updated successfully!\nDeal ID: {deal_id}"

            return f"Failed to update deal: {result}"

        except Exception as e:
            logger.error(f"Error updating deal: {e}")
            return f"Error: {str(e)}"

    async def _delete_deal(self, args: dict) -> str:
        try:
            deal_id = args["deal_id"]
            result = await self.modules_client.delete_record("Deals", deal_id)
            return f"Deal deleted successfully! ID: {deal_id}"
        except Exception as e:
            logger.error(f"Error deleting deal: {e}")
            return f"Error: {str(e)}"

    async def _search_deals(self, args: dict) -> str:
        try:
            deal_name = args.get("deal_name")
            stage = args.get("stage")
            account_name = args.get("account_name")
            min_amount = args.get("min_amount")
            max_amount = args.get("max_amount")

            conditions = {}
            if deal_name:
                conditions["Deal_Name__contains"] = deal_name
            if stage:
                conditions["Stage"] = stage
            if account_name:
                conditions["Account_Name__contains"] = account_name
            if min_amount is not None:
                conditions["Amount__greater_equal"] = str(min_amount)
            if max_amount is not None:
                conditions["Amount__less_equal"] = str(max_amount)

            if not conditions:
                result = await self.modules_client.get_records("Deals", page=1, per_page=200)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Deals",
                    conditions=conditions,
                    fields=["Deal_Name", "Stage", "Amount", "Closing_Date", "Account_Name"]
                )

            if result.get("data") and len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(result["data"], "Deals")

            formatted = self.search_client.format_search_results(result, "Deals")
            return formatted

        except Exception as e:
            logger.error(f"Error searching deals: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # PRODUCT TOOLS
    # ========================================================================

    async def _create_product(self, args: dict) -> str:
        try:
            product_name = args["product_name"]
            unit_price = args.get("unit_price")
            description = args.get("description")
            product_code = args.get("product_code")

            data = {"Product_Name": product_name}
            if unit_price is not None:
                data["Unit_Price"] = unit_price
            if description:
                data["Description"] = description
            if product_code:
                data["Product_Code"] = product_code

            result = await self.modules_client.create_record("Products", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    product_id = record["details"]["id"]
                    return f"Product created successfully!\nProduct ID: {product_id}"

            return f"Failed to create product: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_product(self, args: dict) -> str:
        try:
            product_id = args["product_id"]
            result = await self.modules_client.get_record(
                "Products",
                product_id,
                fields=["Product_Name", "Unit_Price", "Description", "Product_Code"]
            )

            if result.get("data") and len(result["data"]) > 0:
                product = result["data"][0]
                output = "Product Details:\n\n"
                output += f"Name: {product.get('Product_Name', 'N/A')}\n"
                output += f"Unit Price: ${product.get('Unit_Price', 0):,.2f}\n"
                output += f"Code: {product.get('Product_Code', 'N/A')}\n"
                output += f"Description: {product.get('Description', 'N/A')}\n"
                output += f"ID: {product['id']}"
                return output

            return "Product not found"

        except Exception as e:
            logger.error(f"Error getting product: {e}")
            return f"Error: {str(e)}"

    async def _update_product(self, args: dict) -> str:
        try:
            product_id = args["product_id"]
            product_name = args.get("product_name")
            unit_price = args.get("unit_price")
            description = args.get("description")
            product_code = args.get("product_code")

            data = {}
            if product_name:
                data["Product_Name"] = product_name
            if unit_price is not None:
                data["Unit_Price"] = unit_price
            if description:
                data["Description"] = description
            if product_code:
                data["Product_Code"] = product_code

            if not data:
                return "No fields provided to update"

            result = await self.modules_client.update_record("Products", product_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Product updated successfully!\nProduct ID: {product_id}"

            return f"Failed to update product: {result}"

        except Exception as e:
            logger.error(f"Error updating product: {e}")
            return f"Error: {str(e)}"

    async def _delete_product(self, args: dict) -> str:
        try:
            product_id = args["product_id"]
            result = await self.modules_client.delete_record("Products", product_id)
            return f"Product deleted successfully! ID: {product_id}"
        except Exception as e:
            logger.error(f"Error deleting product: {e}")
            return f"Error: {str(e)}"

    async def _search_products(self, args: dict) -> str:
        try:
            product_name = args.get("product_name")
            product_code = args.get("product_code")
            min_price = args.get("min_price")
            max_price = args.get("max_price")

            conditions = {}
            if product_name:
                conditions["Product_Name__contains"] = product_name
            if product_code:
                conditions["Product_Code"] = product_code
            if min_price is not None:
                conditions["Unit_Price__greater_equal"] = str(min_price)
            if max_price is not None:
                conditions["Unit_Price__less_equal"] = str(max_price)

            if not conditions:
                result = await self.modules_client.get_records("Products", page=1, per_page=200)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Products",
                    conditions=conditions,
                    fields=["Product_Name", "Unit_Price", "Product_Code"]
                )

            if result.get("data") and len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(result["data"], "Products")

            formatted = self.search_client.format_search_results(result, "Products")
            return formatted

        except Exception as e:
            logger.error(f"Error searching products: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # TASK TOOLS
    # ========================================================================

    async def _create_task(self, args: dict) -> str:
        try:
            subject = args["subject"]
            related_to_id = args.get("related_to_id")
            due_date = args.get("due_date")
            priority = args.get("priority", "Normal")
            status = args.get("status", "Not Started")
            description = args.get("description")

            result = await self.activities_client.create_task(
                subject=subject,
                what_id=related_to_id,
                due_date=due_date,
                priority=priority,
                status=status,
                description=description
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    task_id = record["details"]["id"]
                    return f"Task created successfully!\nTask ID: {task_id}\nSubject: {subject}"

            return f"Failed to create task: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_task(self, args: dict) -> str:
        try:
            task_id = args["task_id"]
            result = await self.activities_client.get_task(task_id)

            if result.get("data") and len(result["data"]) > 0:
                task = result["data"][0]
                output = "Task Details:\n\n"
                output += f"Subject: {task.get('Subject', 'N/A')}\n"
                output += f"Status: {task.get('Status', 'N/A')}\n"
                output += f"Priority: {task.get('Priority', 'N/A')}\n"
                output += f"Due Date: {task.get('Due_Date', 'N/A')}\n"
                output += f"Description: {task.get('Description', 'N/A')}\n"
                output += f"ID: {task['id']}"
                return output

            return "Task not found"

        except Exception as e:
            logger.error(f"Error getting task: {e}")
            return f"Error: {str(e)}"

    async def _get_tasks_for_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]

            result = await self.activities_client.get_tasks_for_record(module, record_id)

            if not result.get("data"):
                return f"No tasks found for this {module.rstrip('s').lower()}"

            tasks = result["data"]
            output = f"Found {len(tasks)} task(s):\n\n"

            for i, task in enumerate(tasks, 1):
                output += f"{i}. {task.get('Subject', 'N/A')}\n"
                output += f"   Status: {task.get('Status', 'N/A')}\n"
                output += f"   Priority: {task.get('Priority', 'N/A')}\n"
                output += f"   Due: {task.get('Due_Date', 'N/A')}\n"
                output += f"   ID: {task['id']}\n\n"

            return output

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_pending_tasks(self, args: dict) -> str:
        try:
            record_id = args["record_id"]

            modules_to_check = ["Leads", "Contacts", "Deals", "Accounts"]
            result = None
            found_module = None

            for module in modules_to_check:
                try:
                    logger.debug(f"Attempting to get tasks for {module}/{record_id}")
                    test_result = await self.activities_client.get_tasks_for_record(module, record_id)
                    logger.debug(f"API response for {module}/{record_id}: {test_result}")

                    if test_result and "data" in test_result:
                        result = test_result
                        found_module = module
                        logger.info(f"Successfully retrieved tasks from {module}/{record_id}")
                        break
                except Exception as e:
                    logger.debug(f"Could not get tasks from {module}/{record_id}: {e}")
                    continue

            # Method 2: COQL fallback
            if not result or not found_module:
                logger.warning(f"API endpoint failed for {record_id}, trying COQL fallback")
                try:
                    coql_query = f"SELECT id, Subject, Status, Priority, Due_Date, What_Id FROM Tasks WHERE What_Id = '{record_id}' LIMIT 50"
                    logger.info(f"Executing COQL fallback: {coql_query}")

                    coql_result = await self.search_client.search_by_coql(
                        query=coql_query,
                        page=1,
                        per_page=50
                    )

                    if coql_result and coql_result.get("data") and len(coql_result.get("data", [])) > 0:
                        result = coql_result
                        found_module = "COQL (module unknown)"
                        logger.info(f"COQL fallback found {len(result['data'])} tasks for {record_id}")
                    else:
                        return f"Record ID {record_id} not found in any module, and no tasks found via COQL search."
                except Exception as coql_error:
                    logger.error(f"COQL fallback also failed: {coql_error}")
                    return f"Could not retrieve tasks for record {record_id}. Error: {str(coql_error)}"

            if not result.get("data") or len(result["data"]) == 0:
                return f"Found record in {found_module}, but no tasks are associated with it."

            tasks = result["data"]
            output = f"Found {len(tasks)} task(s) for this record:\n\n"

            for i, task in enumerate(tasks, 1):
                output += f"{i}. {task.get('Subject', 'N/A')}\n"
                output += f"   Status: {task.get('Status', 'N/A')}\n"
                output += f"   Priority: {task.get('Priority', 'N/A')}\n"
                output += f"   Due: {task.get('Due_Date', 'N/A')}\n"

                what_id = task.get('What_Id')
                if what_id:
                    what_id_name = what_id.get('name') if isinstance(what_id, dict) else None
                    what_id_value = what_id.get('id') if isinstance(what_id, dict) else what_id
                    if what_id_name:
                        output += f"   Related to: {what_id_name} (ID: {what_id_value})\n"
                    else:
                        output += f"   Related ID: {what_id_value}\n"

                output += f"   Task ID: {task['id']}\n\n"

            return output

        except Exception as e:
            logger.error(f"Error in get_pending_tasks: {e}")
            return f"Error: {str(e)}"

    async def _check_multiple_leads_for_tasks(self, args: dict) -> str:
        try:
            record_ids = args["record_ids"]

            ids = [rid.strip() for rid in record_ids.split(",") if rid.strip()]

            if len(ids) > 50:
                return f"Too many records ({len(ids)}). Please limit to 50 or fewer to avoid rate limits."

            logger.info(f"Checking {len(ids)} leads for tasks with rate limiting")

            leads_with_tasks = []
            leads_without_tasks = []
            failed_checks = []

            batch_size = 5
            for i in range(0, len(ids), batch_size):
                batch = ids[i:i+batch_size]

                for record_id in batch:
                    try:
                        result = await self.activities_client.get_tasks_for_record("Leads", record_id)

                        if result.get("data") and len(result.get("data", [])) > 0:
                            tasks = result["data"]
                            leads_with_tasks.append({
                                "id": record_id,
                                "task_count": len(tasks),
                                "tasks": tasks
                            })
                        else:
                            leads_without_tasks.append(record_id)

                    except Exception as e:
                        logger.debug(f"Error checking {record_id}: {e}")
                        failed_checks.append(record_id)

                if i + batch_size < len(ids):
                    await asyncio.sleep(0.5)

            output = f"Task Check Results ({len(ids)} leads):\n\n"

            if leads_with_tasks:
                output += f"{len(leads_with_tasks)} lead(s) WITH tasks:\n\n"
                for lead in leads_with_tasks:
                    output += f"- Lead ID {lead['id']}: {lead['task_count']} task(s)\n"
                    for task in lead['tasks'][:3]:
                        output += f"  - {task.get('Subject', 'N/A')} (Due: {task.get('Due_Date', 'N/A')})\n"
                    if lead['task_count'] > 3:
                        output += f"  ... and {lead['task_count'] - 3} more\n"
                    output += "\n"

            if leads_without_tasks:
                output += f"{len(leads_without_tasks)} lead(s) WITHOUT tasks\n\n"

            if failed_checks:
                output += f"{len(failed_checks)} lead(s) could not be checked: {', '.join(failed_checks[:5])}\n"

            return output

        except Exception as e:
            logger.error(f"Error in check_multiple_leads_for_tasks: {e}")
            return f"Error: {str(e)}"

    async def _search_tasks(self, args: dict) -> str:
        try:
            status = args.get("status")
            priority = args.get("priority")
            due_date_start = args.get("due_date_start")
            due_date_end = args.get("due_date_end")
            subject_contains = args.get("subject_contains")
            limit = args.get("limit", 50)

            conditions = {}

            if status and status not in ["", "null", None]:
                conditions["Status"] = status
            if priority and priority not in ["", "null", None]:
                conditions["Priority"] = priority
            if subject_contains and subject_contains not in ["", "null", None]:
                conditions["Subject__contains"] = subject_contains

            # Handle date ranges - use COQL for accurate date range search
            if due_date_start or due_date_end:
                coql_query_parts = ["SELECT id, Subject, Status, Priority, Due_Date, What_Id FROM Tasks"]
                where_clauses = []

                if due_date_start and due_date_end:
                    start_date = due_date_start
                    if len(start_date) == 7:
                        start_date = f"{start_date}-01"

                    end_date = due_date_end
                    if len(end_date) == 7:
                        year, month = end_date.split("-")
                        if month in ["01", "03", "05", "07", "08", "10", "12"]:
                            last_day = "31"
                        elif month in ["04", "06", "09", "11"]:
                            last_day = "30"
                        else:
                            year_int = int(year)
                            if year_int % 4 == 0 and (year_int % 100 != 0 or year_int % 400 == 0):
                                last_day = "29"
                            else:
                                last_day = "28"
                        end_date = f"{end_date}-{last_day}"

                    where_clauses.append(f"Due_Date >= '{start_date}' AND Due_Date <= '{end_date}'")
                elif due_date_start:
                    start_date = due_date_start
                    if len(start_date) == 7:
                        start_date = f"{start_date}-01"
                    where_clauses.append(f"Due_Date >= '{start_date}'")
                elif due_date_end:
                    end_date = due_date_end
                    if len(end_date) == 7:
                        year, month = end_date.split("-")
                        if month in ["01", "03", "05", "07", "08", "10", "12"]:
                            last_day = "31"
                        elif month in ["04", "06", "09", "11"]:
                            last_day = "30"
                        else:
                            year_int = int(year)
                            if year_int % 4 == 0 and (year_int % 100 != 0 or year_int % 400 == 0):
                                last_day = "29"
                            else:
                                last_day = "28"
                        end_date = f"{end_date}-{last_day}"
                    where_clauses.append(f"Due_Date <= '{end_date}'")

                if status and status not in ["", "null", None]:
                    status_escaped = status.replace("'", "\\'")
                    where_clauses.append(f"Status = '{status_escaped}'")
                if priority and priority not in ["", "null", None]:
                    priority_escaped = priority.replace("'", "\\'")
                    where_clauses.append(f"Priority = '{priority_escaped}'")
                if subject_contains and subject_contains not in ["", "null", None]:
                    subject_escaped = subject_contains.replace("'", "\\'")
                    where_clauses.append(f"Subject LIKE '%{subject_escaped}%'")

                if where_clauses:
                    coql_query_parts.append("WHERE " + " AND ".join(where_clauses))

                coql_query_parts.append(f" LIMIT {limit}")

                coql_query = " ".join(coql_query_parts)
                logger.info(f"Executing COQL query: {coql_query}")

                try:
                    result = await self.search_client.search_by_coql(
                        query=coql_query,
                        page=1,
                        per_page=limit
                    )
                except Exception as coql_error:
                    logger.warning(f"COQL query failed: {coql_error}. Trying with date-only filter and client-side filtering.")

                    simple_query_parts = ["SELECT id, Subject, Status, Priority, Due_Date, What_Id FROM Tasks"]
                    date_where_clauses = []

                    if due_date_start and due_date_end:
                        date_where_clauses.append(f"Due_Date >= '{start_date}' AND Due_Date <= '{end_date}'")
                    elif due_date_start:
                        date_where_clauses.append(f"Due_Date >= '{start_date}'")
                    elif due_date_end:
                        date_where_clauses.append(f"Due_Date <= '{end_date}'")

                    if date_where_clauses:
                        simple_query_parts.append("WHERE " + " AND ".join(date_where_clauses))

                    simple_query_parts.append(f" LIMIT 200")
                    simple_query = " ".join(simple_query_parts)

                    logger.info(f"Executing simplified COQL query: {simple_query}")
                    result = await self.search_client.search_by_coql(
                        query=simple_query,
                        page=1,
                        per_page=200
                    )

                    if result.get("data"):
                        filtered_tasks = []
                        for task in result["data"]:
                            if status and status not in ["", "null", None]:
                                if task.get("Status") != status:
                                    continue
                            if priority and priority not in ["", "null", None]:
                                if task.get("Priority") != priority:
                                    continue
                            if subject_contains and subject_contains not in ["", "null", None]:
                                if subject_contains.lower() not in str(task.get("Subject", "")).lower():
                                    continue
                            filtered_tasks.append(task)
                            if len(filtered_tasks) >= limit:
                                break
                        result["data"] = filtered_tasks
                        logger.info(f"Client-side filtering: {len(result.get('data', []))} tasks matched")

            elif not conditions:
                result = await self.modules_client.get_records(
                    "Tasks",
                    fields=["Subject", "Status", "Priority", "Due_Date", "What_Id"],
                    page=1,
                    per_page=limit
                )
            else:
                logger.info(f"Searching tasks with conditions: {conditions}")
                result = await self.search_client.search_by_conditions(
                    module="Tasks",
                    conditions=conditions,
                    fields=["Subject", "Status", "Priority", "Due_Date", "What_Id"],
                    page=1,
                    per_page=limit
                )

            if not result.get("data") or len(result["data"]) == 0:
                return "No tasks found matching the criteria"

            tasks = result["data"]

            if len(tasks) > self.LARGE_RESULT_THRESHOLD:
                return self._cache_and_summarize(tasks, "Tasks")

            output = f"Found {len(tasks)} task(s):\n\n"

            for i, task in enumerate(tasks, 1):
                output += f"{i}. {task.get('Subject', 'N/A')}\n"
                output += f"   Status: {task.get('Status', 'N/A')}\n"
                output += f"   Priority: {task.get('Priority', 'N/A')}\n"
                output += f"   Due: {task.get('Due_Date', 'N/A')}\n"

                what_id = task.get('What_Id')
                if what_id:
                    what_id_name = what_id.get('name') if isinstance(what_id, dict) else None
                    what_id_value = what_id.get('id') if isinstance(what_id, dict) else what_id
                    if what_id_name:
                        output += f"   Related to: {what_id_name} (ID: {what_id_value})\n"
                    else:
                        output += f"   Related ID: {what_id_value}\n"

                output += f"   Task ID: {task['id']}\n\n"

            return output

        except Exception as e:
            logger.error(f"Error searching tasks: {e}")
            return f"Error: {str(e)}"

    async def _update_task(self, args: dict) -> str:
        try:
            task_id = args["task_id"]
            subject = args.get("subject")
            status = args.get("status")
            priority = args.get("priority")
            due_date = args.get("due_date")
            description = args.get("description")

            result = await self.activities_client.update_task(
                task_id=task_id,
                subject=subject,
                status=status,
                priority=priority,
                due_date=due_date,
                description=description
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Task updated successfully!\nTask ID: {task_id}"

            return f"Failed to update task: {result}"

        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return f"Error: {str(e)}"

    async def _delete_task(self, args: dict) -> str:
        try:
            task_id = args["task_id"]
            result = await self.activities_client.delete_task(task_id)
            return f"Task deleted successfully! ID: {task_id}"
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # EVENT TOOLS
    # ========================================================================

    async def _create_event(self, args: dict) -> str:
        try:
            event_title = args["event_title"]
            start_datetime = args["start_datetime"]
            end_datetime = args["end_datetime"]
            related_to_id = args.get("related_to_id")
            description = args.get("description")

            result = await self.activities_client.create_event(
                event_title=event_title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                what_id=related_to_id,
                description=description
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    event_id = record["details"]["id"]
                    return f"Event created successfully!\nEvent ID: {event_id}\nTitle: {event_title}"

            return f"Failed to create event: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_event(self, args: dict) -> str:
        try:
            event_id = args["event_id"]
            result = await self.activities_client.get_event(event_id)

            if result.get("data") and len(result["data"]) > 0:
                event = result["data"][0]
                output = "Event Details:\n\n"
                output += f"Title: {event.get('Event_Title', 'N/A')}\n"
                output += f"Start: {event.get('Start_DateTime', 'N/A')}\n"
                output += f"End: {event.get('End_DateTime', 'N/A')}\n"
                output += f"Description: {event.get('Description', 'N/A')}\n"
                output += f"ID: {event['id']}"
                return output

            return "Event not found"

        except Exception as e:
            logger.error(f"Error getting event: {e}")
            return f"Error: {str(e)}"

    async def _get_events_for_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]

            result = await self.activities_client.get_events_for_record(module, record_id)

            if not result.get("data"):
                return f"No events found for this {module.rstrip('s').lower()}"

            events = result["data"]
            output = f"Found {len(events)} event(s):\n\n"

            for i, event in enumerate(events, 1):
                output += f"{i}. {event.get('Event_Title', 'N/A')}\n"
                output += f"   Start: {event.get('Start_DateTime', 'N/A')}\n"
                output += f"   End: {event.get('End_DateTime', 'N/A')}\n"
                output += f"   ID: {event['id']}\n\n"

            return output

        except Exception as e:
            return f"Error: {str(e)}"

    async def _update_event(self, args: dict) -> str:
        try:
            event_id = args["event_id"]
            event_title = args.get("event_title")
            start_datetime = args.get("start_datetime")
            end_datetime = args.get("end_datetime")
            description = args.get("description")

            result = await self.activities_client.update_event(
                event_id=event_id,
                event_title=event_title,
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description=description
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Event updated successfully!\nEvent ID: {event_id}"

            return f"Failed to update event: {result}"

        except Exception as e:
            logger.error(f"Error updating event: {e}")
            return f"Error: {str(e)}"

    async def _delete_event(self, args: dict) -> str:
        try:
            event_id = args["event_id"]
            result = await self.activities_client.delete_event(event_id)
            return f"Event deleted successfully! ID: {event_id}"
        except Exception as e:
            logger.error(f"Error deleting event: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # CALL TOOLS
    # ========================================================================

    async def _create_call(self, args: dict) -> str:
        try:
            subject = args["subject"]
            call_type = args["call_type"]
            related_to_id = args.get("related_to_id")
            call_start_time = args.get("call_start_time")
            call_duration = args.get("call_duration")
            description = args.get("description")

            result = await self.activities_client.create_call(
                subject=subject,
                call_type=call_type,
                what_id=related_to_id,
                call_start_time=call_start_time,
                call_duration=call_duration,
                description=description
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    call_id = record["details"]["id"]
                    return f"Call logged successfully!\nCall ID: {call_id}\nSubject: {subject}"

            return f"Failed to log call: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_call(self, args: dict) -> str:
        try:
            call_id = args["call_id"]
            result = await self.activities_client.get_call(call_id)

            if result.get("data") and len(result["data"]) > 0:
                call = result["data"][0]
                output = "Call Details:\n\n"
                output += f"Subject: {call.get('Subject', 'N/A')}\n"
                output += f"Type: {call.get('Call_Type', 'N/A')}\n"
                output += f"Start Time: {call.get('Call_Start_Time', 'N/A')}\n"
                output += f"Duration: {call.get('Call_Duration', 'N/A')} min\n"
                output += f"Description: {call.get('Description', 'N/A')}\n"
                output += f"ID: {call['id']}"
                return output

            return "Call not found"

        except Exception as e:
            logger.error(f"Error getting call: {e}")
            return f"Error: {str(e)}"

    async def _update_call(self, args: dict) -> str:
        try:
            call_id = args["call_id"]
            subject = args.get("subject")
            call_type = args.get("call_type")
            call_start_time = args.get("call_start_time")
            call_duration = args.get("call_duration")
            description = args.get("description")

            result = await self.activities_client.update_call(
                call_id=call_id,
                subject=subject,
                call_type=call_type,
                call_start_time=call_start_time,
                call_duration=call_duration,
                description=description
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Call updated successfully!\nCall ID: {call_id}"

            return f"Failed to update call: {result}"

        except Exception as e:
            logger.error(f"Error updating call: {e}")
            return f"Error: {str(e)}"

    async def _delete_call(self, args: dict) -> str:
        try:
            call_id = args["call_id"]
            result = await self.activities_client.delete_call(call_id)
            return f"Call deleted successfully! ID: {call_id}"
        except Exception as e:
            logger.error(f"Error deleting call: {e}")
            return f"Error: {str(e)}"

    async def _get_calls_for_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            limit = args.get("limit", 20)

            conditions = {"What_Id": record_id}

            result = await self.search_client.search_by_conditions(
                module="Calls",
                conditions=conditions,
                page=1,
                per_page=limit
            )

            if result.get("data") and len(result["data"]) > 0:
                output = f"Found {len(result['data'])} call(s) for this record:\n\n"
                for call in result["data"]:
                    output += f"- Subject: {call.get('Subject', 'N/A')}\n"
                    output += f"  Call Type: {call.get('Call_Type', 'N/A')}\n"
                    output += f"  Duration: {call.get('Call_Duration', 'N/A')}\n"
                    output += f"  Status: {call.get('Call_Status', 'N/A')}\n"
                    output += f"  ID: {call['id']}\n\n"
                return output

            return "No calls found for this record"

        except Exception as e:
            logger.error(f"Error getting calls for record: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # NOTE TOOLS
    # ========================================================================

    async def _create_note(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            title = args["title"]
            content = args["content"]

            result = await self.notes_client.create_note(module, record_id, title, content)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    note_id = record["details"]["id"]
                    return f"Note created successfully!\nNote ID: {note_id}\nTitle: {title}"

            return f"Failed to create note: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_notes_for_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]

            result = await self.notes_client.get_notes(module, record_id)

            if not result.get("data"):
                return f"No notes found for this {module.rstrip('s').lower()}"

            notes = result["data"]
            output = f"Found {len(notes)} note(s):\n\n"

            for i, note in enumerate(notes, 1):
                output += f"{i}. {note.get('Note_Title', 'Untitled')}\n"
                output += f"   {note.get('Note_Content', '')}\n"
                output += f"   Created: {note.get('Created_Time', 'N/A')}\n"
                output += f"   ID: {note['id']}\n\n"

            return output

        except Exception as e:
            return f"Error: {str(e)}"

    async def _update_note(self, args: dict) -> str:
        try:
            note_id = args["note_id"]
            title = args.get("title")
            content = args.get("content")

            result = await self.notes_client.update_note(
                note_id=note_id,
                title=title,
                content=content
            )

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Note updated successfully!\nNote ID: {note_id}"

            return f"Failed to update note: {result}"

        except Exception as e:
            logger.error(f"Error updating note: {e}")
            return f"Error: {str(e)}"

    async def _delete_note(self, args: dict) -> str:
        try:
            note_id = args["note_id"]
            result = await self.notes_client.delete_note(note_id)
            return f"Note deleted successfully! ID: {note_id}"
        except Exception as e:
            logger.error(f"Error deleting note: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # VENDOR TOOLS
    # ========================================================================

    async def _create_vendor(self, args: dict) -> str:
        try:
            vendor_name = args["vendor_name"]
            email = args.get("email")
            phone = args.get("phone")
            website = args.get("website")

            data = {"Vendor_Name": vendor_name}
            if email:
                data["Email"] = email
            if phone:
                data["Phone"] = phone
            if website:
                data["Website"] = website

            result = await self.modules_client.create_record("Vendors", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    vendor_id = record["details"]["id"]
                    return f"Vendor created successfully!\nVendor ID: {vendor_id}\nName: {vendor_name}"

            return f"Failed to create vendor: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_vendor(self, args: dict) -> str:
        try:
            vendor_id = args["vendor_id"]
            result = await self.modules_client.get_record(
                "Vendors",
                vendor_id,
                fields=["Vendor_Name", "Email", "Phone", "Website"]
            )

            if result.get("data") and len(result["data"]) > 0:
                vendor = result["data"][0]
                output = "Vendor Details:\n\n"
                output += f"Name: {vendor.get('Vendor_Name', 'N/A')}\n"
                output += f"Email: {vendor.get('Email', 'N/A')}\n"
                output += f"Phone: {vendor.get('Phone', 'N/A')}\n"
                output += f"Website: {vendor.get('Website', 'N/A')}\n"
                output += f"ID: {vendor['id']}"
                return output

            return "Vendor not found"

        except Exception as e:
            logger.error(f"Error getting vendor: {e}")
            return f"Error: {str(e)}"

    async def _update_vendor(self, args: dict) -> str:
        try:
            vendor_id = args["vendor_id"]
            vendor_name = args.get("vendor_name")
            email = args.get("email")
            phone = args.get("phone")
            website = args.get("website")

            data = {}
            if vendor_name:
                data["Vendor_Name"] = vendor_name
            if email:
                data["Email"] = email
            if phone:
                data["Phone"] = phone
            if website:
                data["Website"] = website

            if not data:
                return "No fields to update"

            result = await self.modules_client.update_record("Vendors", vendor_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Vendor updated successfully! ID: {vendor_id}"

            return f"Failed to update vendor: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _delete_vendor(self, args: dict) -> str:
        try:
            vendor_id = args["vendor_id"]
            result = await self.modules_client.delete_record("Vendors", vendor_id)
            return f"Vendor deleted successfully! ID: {vendor_id}"
        except Exception as e:
            logger.error(f"Error deleting vendor: {e}")
            return f"Error: {str(e)}"

    async def _search_vendors(self, args: dict) -> str:
        try:
            vendor_name = args.get("vendor_name")
            email = args.get("email")
            limit = args.get("limit", 10)

            conditions = {}
            if vendor_name:
                conditions["Vendor_Name__contains"] = vendor_name
            if email:
                conditions["Email"] = email

            if not conditions:
                result = await self.modules_client.get_records("Vendors", page=1, per_page=limit)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Vendors",
                    conditions=conditions,
                    page=1,
                    per_page=limit
                )

            if result.get("data") and len(result["data"]) > 0:
                if len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(result["data"], "Vendors")

                output = f"Found {len(result['data'])} vendor(s):\n\n"
                for vendor in result["data"]:
                    output += f"- {vendor.get('Vendor_Name', 'N/A')} (ID: {vendor['id']})\n"
                    output += f"  Email: {vendor.get('Email', 'N/A')}\n\n"
                return output

            return "No vendors found"

        except Exception as e:
            logger.error(f"Error searching vendors: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # QUOTE TOOLS
    # ========================================================================

    async def _create_quote(self, args: dict) -> str:
        try:
            subject = args["subject"]
            deal_name = args.get("deal_name")
            account_name = args.get("account_name")
            quote_stage = args.get("quote_stage")

            data = {"Subject": subject}
            if deal_name:
                data["Deal_Name"] = deal_name
            if account_name:
                data["Account_Name"] = account_name
            if quote_stage:
                data["Quote_Stage"] = quote_stage

            result = await self.modules_client.create_record("Quotes", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    quote_id = record["details"]["id"]
                    return f"Quote created successfully!\nQuote ID: {quote_id}\nSubject: {subject}"

            return f"Failed to create quote: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_quote(self, args: dict) -> str:
        try:
            quote_id = args["quote_id"]
            result = await self.modules_client.get_record(
                "Quotes",
                quote_id,
                fields=["Subject", "Deal_Name", "Account_Name", "Quote_Stage", "Grand_Total"]
            )

            if result.get("data") and len(result["data"]) > 0:
                quote = result["data"][0]
                output = "Quote Details:\n\n"
                output += f"Subject: {quote.get('Subject', 'N/A')}\n"
                output += f"Stage: {quote.get('Quote_Stage', 'N/A')}\n"
                output += f"Deal: {quote.get('Deal_Name', 'N/A')}\n"
                output += f"Account: {quote.get('Account_Name', 'N/A')}\n"
                output += f"Grand Total: ${quote.get('Grand_Total', 0):,.2f}\n"
                output += f"ID: {quote['id']}"
                return output

            return "Quote not found"

        except Exception as e:
            logger.error(f"Error getting quote: {e}")
            return f"Error: {str(e)}"

    async def _update_quote(self, args: dict) -> str:
        try:
            quote_id = args["quote_id"]
            subject = args.get("subject")
            quote_stage = args.get("quote_stage")

            data = {}
            if subject:
                data["Subject"] = subject
            if quote_stage:
                data["Quote_Stage"] = quote_stage

            if not data:
                return "No fields to update"

            result = await self.modules_client.update_record("Quotes", quote_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Quote updated successfully! ID: {quote_id}"

            return f"Failed to update quote: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _delete_quote(self, args: dict) -> str:
        try:
            quote_id = args["quote_id"]
            result = await self.modules_client.delete_record("Quotes", quote_id)
            return f"Quote deleted successfully! ID: {quote_id}"
        except Exception as e:
            logger.error(f"Error deleting quote: {e}")
            return f"Error: {str(e)}"

    async def _search_quotes(self, args: dict) -> str:
        try:
            subject = args.get("subject")
            quote_stage = args.get("quote_stage")
            limit = args.get("limit", 10)

            conditions = {}
            if subject:
                conditions["Subject__contains"] = subject
            if quote_stage:
                conditions["Quote_Stage"] = quote_stage

            if not conditions:
                result = await self.modules_client.get_records("Quotes", page=1, per_page=limit)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Quotes",
                    conditions=conditions,
                    page=1,
                    per_page=limit
                )

            if result.get("data") and len(result["data"]) > 0:
                if len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(result["data"], "Quotes")

                output = f"Found {len(result['data'])} quote(s):\n\n"
                for quote in result["data"]:
                    output += f"- {quote.get('Subject', 'N/A')} (ID: {quote['id']})\n"
                    output += f"  Stage: {quote.get('Quote_Stage', 'N/A')}\n\n"
                return output

            return "No quotes found"

        except Exception as e:
            logger.error(f"Error searching quotes: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # SALES ORDER TOOLS
    # ========================================================================

    async def _create_sales_order(self, args: dict) -> str:
        try:
            subject = args["subject"]
            account_name = args.get("account_name")
            status = args.get("status")

            data = {"Subject": subject}
            if account_name:
                data["Account_Name"] = account_name
            if status:
                data["Status"] = status

            result = await self.modules_client.create_record("Sales_Orders", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    so_id = record["details"]["id"]
                    return f"Sales Order created successfully!\nSales Order ID: {so_id}\nSubject: {subject}"

            return f"Failed to create sales order: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_sales_order(self, args: dict) -> str:
        try:
            sales_order_id = args["sales_order_id"]
            result = await self.modules_client.get_record(
                "Sales_Orders",
                sales_order_id,
                fields=["Subject", "Account_Name", "Status", "Grand_Total"]
            )

            if result.get("data") and len(result["data"]) > 0:
                so = result["data"][0]
                output = "Sales Order Details:\n\n"
                output += f"Subject: {so.get('Subject', 'N/A')}\n"
                output += f"Status: {so.get('Status', 'N/A')}\n"
                output += f"Account: {so.get('Account_Name', 'N/A')}\n"
                output += f"Grand Total: ${so.get('Grand_Total', 0):,.2f}\n"
                output += f"ID: {so['id']}"
                return output

            return "Sales Order not found"

        except Exception as e:
            logger.error(f"Error getting sales order: {e}")
            return f"Error: {str(e)}"

    async def _update_sales_order(self, args: dict) -> str:
        try:
            sales_order_id = args["sales_order_id"]
            subject = args.get("subject")
            status = args.get("status")

            data = {}
            if subject:
                data["Subject"] = subject
            if status:
                data["Status"] = status

            if not data:
                return "No fields to update"

            result = await self.modules_client.update_record("Sales_Orders", sales_order_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Sales Order updated successfully! ID: {sales_order_id}"

            return f"Failed to update sales order: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _delete_sales_order(self, args: dict) -> str:
        try:
            sales_order_id = args["sales_order_id"]
            result = await self.modules_client.delete_record("Sales_Orders", sales_order_id)
            return f"Sales Order deleted successfully! ID: {sales_order_id}"
        except Exception as e:
            logger.error(f"Error deleting sales order: {e}")
            return f"Error: {str(e)}"

    async def _search_sales_orders(self, args: dict) -> str:
        try:
            subject = args.get("subject")
            status = args.get("status")
            limit = args.get("limit", 10)

            conditions = {}
            if subject:
                conditions["Subject__contains"] = subject
            if status:
                conditions["Status"] = status

            if not conditions:
                result = await self.modules_client.get_records("Sales_Orders", page=1, per_page=limit)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Sales_Orders",
                    conditions=conditions,
                    page=1,
                    per_page=limit
                )

            if result.get("data") and len(result["data"]) > 0:
                if len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(result["data"], "Sales_Orders")

                output = f"Found {len(result['data'])} sales order(s):\n\n"
                for so in result["data"]:
                    output += f"- {so.get('Subject', 'N/A')} (ID: {so['id']})\n"
                    output += f"  Status: {so.get('Status', 'N/A')}\n\n"
                return output

            return "No sales orders found"

        except Exception as e:
            logger.error(f"Error searching sales orders: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # PURCHASE ORDER TOOLS
    # ========================================================================

    async def _create_purchase_order(self, args: dict) -> str:
        try:
            subject = args["subject"]
            vendor_name = args.get("vendor_name")
            status = args.get("status")

            data = {"Subject": subject}
            if vendor_name:
                data["Vendor_Name"] = vendor_name
            if status:
                data["Status"] = status

            result = await self.modules_client.create_record("Purchase_Orders", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    po_id = record["details"]["id"]
                    return f"Purchase Order created successfully!\nPurchase Order ID: {po_id}\nSubject: {subject}"

            return f"Failed to create purchase order: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_purchase_order(self, args: dict) -> str:
        try:
            purchase_order_id = args["purchase_order_id"]
            result = await self.modules_client.get_record(
                "Purchase_Orders",
                purchase_order_id,
                fields=["Subject", "Vendor_Name", "Status", "Grand_Total"]
            )

            if result.get("data") and len(result["data"]) > 0:
                po = result["data"][0]
                output = "Purchase Order Details:\n\n"
                output += f"Subject: {po.get('Subject', 'N/A')}\n"
                output += f"Status: {po.get('Status', 'N/A')}\n"
                output += f"Vendor: {po.get('Vendor_Name', 'N/A')}\n"
                output += f"Grand Total: ${po.get('Grand_Total', 0):,.2f}\n"
                output += f"ID: {po['id']}"
                return output

            return "Purchase Order not found"

        except Exception as e:
            logger.error(f"Error getting purchase order: {e}")
            return f"Error: {str(e)}"

    async def _update_purchase_order(self, args: dict) -> str:
        try:
            purchase_order_id = args["purchase_order_id"]
            subject = args.get("subject")
            status = args.get("status")

            data = {}
            if subject:
                data["Subject"] = subject
            if status:
                data["Status"] = status

            if not data:
                return "No fields to update"

            result = await self.modules_client.update_record("Purchase_Orders", purchase_order_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Purchase Order updated successfully! ID: {purchase_order_id}"

            return f"Failed to update purchase order: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _delete_purchase_order(self, args: dict) -> str:
        try:
            purchase_order_id = args["purchase_order_id"]
            result = await self.modules_client.delete_record("Purchase_Orders", purchase_order_id)
            return f"Purchase Order deleted successfully! ID: {purchase_order_id}"
        except Exception as e:
            logger.error(f"Error deleting purchase order: {e}")
            return f"Error: {str(e)}"

    async def _search_purchase_orders(self, args: dict) -> str:
        try:
            subject = args.get("subject")
            status = args.get("status")
            limit = args.get("limit", 10)

            conditions = {}
            if subject:
                conditions["Subject__contains"] = subject
            if status:
                conditions["Status"] = status

            if not conditions:
                result = await self.modules_client.get_records("Purchase_Orders", page=1, per_page=limit)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Purchase_Orders",
                    conditions=conditions,
                    page=1,
                    per_page=limit
                )

            if result.get("data") and len(result["data"]) > 0:
                if len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(result["data"], "Purchase_Orders")

                output = f"Found {len(result['data'])} purchase order(s):\n\n"
                for po in result["data"]:
                    output += f"- {po.get('Subject', 'N/A')} (ID: {po['id']})\n"
                    output += f"  Status: {po.get('Status', 'N/A')}\n\n"
                return output

            return "No purchase orders found"

        except Exception as e:
            logger.error(f"Error searching purchase orders: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # INVOICE TOOLS
    # ========================================================================

    async def _create_invoice(self, args: dict) -> str:
        try:
            subject = args["subject"]
            account_name = args.get("account_name")
            status = args.get("status")

            data = {"Subject": subject}
            if account_name:
                data["Account_Name"] = account_name
            if status:
                data["Status"] = status

            result = await self.modules_client.create_record("Invoices", data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    invoice_id = record["details"]["id"]
                    return f"Invoice created successfully!\nInvoice ID: {invoice_id}\nSubject: {subject}"

            return f"Failed to create invoice: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_invoice(self, args: dict) -> str:
        try:
            invoice_id = args["invoice_id"]
            result = await self.modules_client.get_record(
                "Invoices",
                invoice_id,
                fields=["Subject", "Account_Name", "Status", "Grand_Total"]
            )

            if result.get("data") and len(result["data"]) > 0:
                invoice = result["data"][0]
                output = "Invoice Details:\n\n"
                output += f"Subject: {invoice.get('Subject', 'N/A')}\n"
                output += f"Status: {invoice.get('Status', 'N/A')}\n"
                output += f"Account: {invoice.get('Account_Name', 'N/A')}\n"
                output += f"Grand Total: ${invoice.get('Grand_Total', 0):,.2f}\n"
                output += f"ID: {invoice['id']}"
                return output

            return "Invoice not found"

        except Exception as e:
            logger.error(f"Error getting invoice: {e}")
            return f"Error: {str(e)}"

    async def _update_invoice(self, args: dict) -> str:
        try:
            invoice_id = args["invoice_id"]
            subject = args.get("subject")
            status = args.get("status")

            data = {}
            if subject:
                data["Subject"] = subject
            if status:
                data["Status"] = status

            if not data:
                return "No fields to update"

            result = await self.modules_client.update_record("Invoices", invoice_id, data)

            if result.get("data") and len(result["data"]) > 0:
                record = result["data"][0]
                if record.get("code") == "SUCCESS":
                    return f"Invoice updated successfully! ID: {invoice_id}"

            return f"Failed to update invoice: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _delete_invoice(self, args: dict) -> str:
        try:
            invoice_id = args["invoice_id"]
            result = await self.modules_client.delete_record("Invoices", invoice_id)
            return f"Invoice deleted successfully! ID: {invoice_id}"
        except Exception as e:
            logger.error(f"Error deleting invoice: {e}")
            return f"Error: {str(e)}"

    async def _search_invoices(self, args: dict) -> str:
        try:
            subject = args.get("subject")
            status = args.get("status")
            limit = args.get("limit", 10)

            conditions = {}
            if subject:
                conditions["Subject__contains"] = subject
            if status:
                conditions["Status"] = status

            if not conditions:
                result = await self.modules_client.get_records("Invoices", page=1, per_page=limit)
            else:
                result = await self.search_client.search_by_conditions(
                    module="Invoices",
                    conditions=conditions,
                    page=1,
                    per_page=limit
                )

            if result.get("data") and len(result["data"]) > 0:
                if len(result["data"]) > self.LARGE_RESULT_THRESHOLD:
                    return self._cache_and_summarize(result["data"], "Invoices")

                output = f"Found {len(result['data'])} invoice(s):\n\n"
                for invoice in result["data"]:
                    output += f"- {invoice.get('Subject', 'N/A')} (ID: {invoice['id']})\n"
                    output += f"  Status: {invoice.get('Status', 'N/A')}\n\n"
                return output

            return "No invoices found"

        except Exception as e:
            logger.error(f"Error searching invoices: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # HEALTH CHECK
    # ========================================================================

    async def _zoho_health_check(self, args: dict) -> str:
        try:
            is_healthy = await self.modules_client.health_check()

            if is_healthy:
                return "Zoho CRM API is healthy and accessible"
            else:
                return "Zoho CRM API is not responding"

        except Exception as e:
            return f"Health check failed: {str(e)}"

    # ========================================================================
    # ADVANCED: FILE TOOLS
    # ========================================================================

    async def _upload_file_to_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            file_path = args["file_path"]

            result = await self.files_client.upload_file(module, record_id, file_path)

            if result.get("data"):
                attachment_id = result["data"][0]["details"]["id"]
                return f"File uploaded successfully!\nAttachment ID: {attachment_id}\nAttached to {module}: {record_id}"

            return f"Failed to upload file: {result}"

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            return f"Error: {str(e)}"

    async def _get_record_attachments(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]

            result = await self.files_client.get_attachments(module, record_id)

            if result.get("data"):
                output = f"Attachments for {module} {record_id}:\n\n"
                for attachment in result["data"]:
                    output += f"- {attachment.get('File_Name', 'Unknown')}\n"
                    output += f"  Size: {attachment.get('Size', 0)} bytes\n"
                    output += f"  ID: {attachment['id']}\n\n"
                return output

            return "No attachments found"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: EMAIL TOOLS
    # ========================================================================

    async def _send_email_from_crm(self, args: dict) -> str:
        try:
            to_emails = args["to_emails"]
            from_email = args["from_email"]
            subject = args["subject"]
            content = args["content"]
            cc_emails = args.get("cc_emails")

            result = await self.emails_client.send_email(
                to_emails=to_emails,
                from_email=from_email,
                subject=subject,
                content=content,
                cc_emails=cc_emails
            )

            if result.get("data"):
                return f"Email sent successfully!\nTo: {', '.join(to_emails)}\nSubject: {subject}"

            return f"Failed to send email: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _send_email_to_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            from_email = args["from_email"]
            subject = args["subject"]
            content = args["content"]

            result = await self.emails_client.send_email_to_record(
                module=module,
                record_id=record_id,
                from_email=from_email,
                subject=subject,
                content=content
            )

            if result.get("data"):
                return f"Email sent to {module} record {record_id}!\nSubject: {subject}"

            return f"Failed to send email: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_email_templates(self, args: dict) -> str:
        try:
            module = args.get("module")
            result = await self.emails_client.get_email_templates(module)

            if result.get("email_templates"):
                templates = result["email_templates"]
                output = f"Found {len(templates)} email template(s):\n\n"
                for tmpl in templates:
                    output += f"- {tmpl.get('name', 'N/A')}\n"
                    output += f"  ID: {tmpl.get('id', 'N/A')}\n"
                    output += f"  Subject: {tmpl.get('subject', 'N/A')}\n"
                    if tmpl.get("module"):
                        output += f"  Module: {tmpl['module'].get('api_name', 'N/A')}\n"
                    output += f"  Folder: {tmpl.get('folder', {}).get('name', 'N/A')}\n\n"
                return output

            return "No email templates found"

        except Exception as e:
            logger.error(f"Error getting email templates: {e}")
            return f"Error: {str(e)}"

    async def _send_email_with_template(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            template_id = args["template_id"]
            from_email = args["from_email"]

            result = await self.emails_client.send_email_with_template(
                module=module,
                record_id=record_id,
                template_id=template_id,
                from_email=from_email,
            )

            if result.get("data"):
                return f"Email sent using template!\nTemplate ID: {template_id}\nTo: {module} record {record_id}"

            return f"Failed to send email with template: {result}"

        except Exception as e:
            logger.error(f"Error sending email with template: {e}")
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: BULK OPERATIONS
    # ========================================================================

    async def _bulk_create_records(self, args: dict) -> str:
        try:
            module = args["module"]
            records_json = args["records_json"]
            trigger_workflow = args.get("trigger_workflow", False)

            records = json.loads(records_json)

            if len(records) > 100:
                return "Maximum 100 records per bulk operation"

            result = await self.bulk_client.bulk_create(module, records, trigger_workflow)

            if result.get("data"):
                success_count = sum(1 for r in result["data"] if r.get("code") == "SUCCESS")
                return f"Bulk create complete!\nCreated: {success_count}/{len(records)} records in {module}"

            return f"Bulk create failed: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _bulk_update_records(self, args: dict) -> str:
        try:
            module = args["module"]
            records_json = args["records_json"]
            trigger_workflow = args.get("trigger_workflow", False)

            records = json.loads(records_json)

            if len(records) > 100:
                return "Maximum 100 records per bulk operation"

            result = await self.bulk_client.bulk_update(module, records, trigger_workflow)

            if result.get("data"):
                success_count = sum(1 for r in result["data"] if r.get("code") == "SUCCESS")
                return f"Bulk update complete!\nUpdated: {success_count}/{len(records)} records in {module}"

            return f"Bulk update failed: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _bulk_delete_records(self, args: dict) -> str:
        try:
            module = args["module"]
            record_ids = args["record_ids"]

            if len(record_ids) > 100:
                return "Maximum 100 records per bulk operation"

            result = await self.bulk_client.bulk_delete(module, record_ids)

            if result.get("data"):
                success_count = sum(1 for r in result["data"] if r.get("code") == "SUCCESS")
                return f"Bulk delete complete!\nDeleted: {success_count}/{len(record_ids)} records from {module}"

            return f"Bulk delete failed: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: CUSTOM MODULES
    # ========================================================================

    async def _discover_all_modules(self, args: dict) -> str:
        try:
            result = await self.custom_modules_client.get_all_modules()

            if result.get("modules"):
                output = "Available CRM Modules:\n\n"
                for module in result["modules"]:
                    api_name = module.get("api_name", "Unknown")
                    module_name = module.get("module_name", api_name)
                    output += f"- {module_name} (API: {api_name})\n"
                return output

            return "No modules found"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_module_fields(self, args: dict) -> str:
        try:
            module = args["module"]
            result = await self.custom_modules_client.get_module_fields(module)

            if result.get("fields"):
                output = f"Fields in {module}:\n\n"
                for field in result["fields"][:20]:
                    field_label = field.get("field_label", "Unknown")
                    api_name = field.get("api_name", "Unknown")
                    data_type = field.get("data_type", "Unknown")
                    output += f"- {field_label} ({api_name}) - {data_type}\n"

                if len(result["fields"]) > 20:
                    output += f"\n... and {len(result['fields']) - 20} more fields"

                return output

            return "No fields found"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: WORKFLOWS
    # ========================================================================

    async def _get_workflow_rules(self, args: dict) -> str:
        try:
            module = args.get("module")
            result = await self.workflows_client.get_workflow_rules(module)

            if result.get("workflow_rules"):
                output = "Workflow Rules:\n\n"
                for rule in result["workflow_rules"]:
                    output += f"- {rule.get('name', 'Unknown')}\n"
                    output += f"  Module: {rule.get('module', 'N/A')}\n"
                    output += f"  ID: {rule['id']}\n\n"
                return output

            return "No workflow rules found"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: BLUEPRINTS
    # ========================================================================

    async def _get_blueprint_for_record(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            result = await self.blueprints_client.get_blueprint(module, record_id)

            if result.get("blueprint"):
                blueprint = result["blueprint"]
                output = f"Blueprint for {module} {record_id}:\n\n"
                output += f"Current State: {blueprint.get('process_info', {}).get('field_label', 'Unknown')}\n\n"

                if blueprint.get("transitions"):
                    output += "Available Transitions:\n"
                    for transition in blueprint["transitions"]:
                        output += f"- {transition.get('name', 'Unknown')}\n"
                        output += f"  To: {transition.get('next_field_value', 'N/A')}\n"
                        output += f"  ID: {transition['id']}\n\n"

                return output

            return "No blueprint found for this record"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: PRICE BOOKS
    # ========================================================================

    async def _create_price_book(self, args: dict) -> str:
        try:
            pricing_name = args["pricing_name"]
            description = args.get("description")

            result = await self.pricebooks_client.create_price_book(pricing_name, description)

            if result.get("data"):
                price_book_id = result["data"][0]["details"]["id"]
                return f"Price book created!\nName: {pricing_name}\nID: {price_book_id}"

            return f"Failed to create price book: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _get_all_price_books(self, args: dict) -> str:
        try:
            result = await self.pricebooks_client.get_price_books()

            if result.get("data"):
                output = "Price Books:\n\n"
                for pb in result["data"]:
                    output += f"- {pb.get('Pricing_Details__s', 'Unknown')}\n"
                    output += f"  ID: {pb['id']}\n\n"
                return output

            return "No price books found"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: WEBFORMS
    # ========================================================================

    async def _get_webforms(self, args: dict) -> str:
        try:
            module = args.get("module")
            result = await self.webforms_client.get_webforms(module)

            if result.get("web_forms"):
                output = "Web Forms:\n\n"
                for form in result["web_forms"]:
                    output += f"- {form.get('name', 'Unknown')}\n"
                    output += f"  Module: {form.get('module', 'N/A')}\n"
                    output += f"  ID: {form['id']}\n\n"
                return output

            return "No web forms found"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: TERRITORIES
    # ========================================================================

    async def _get_territories(self, args: dict) -> str:
        try:
            result = await self.territories_client.get_territories()

            if result.get("territories"):
                output = "Territories:\n\n"
                for territory in result["territories"]:
                    output += f"- {territory.get('name', 'Unknown')}\n"
                    output += f"  ID: {territory['id']}\n\n"
                return output

            return "No territories found"

        except Exception as e:
            return f"Error: {str(e)}"

    async def _assign_territory(self, args: dict) -> str:
        try:
            module = args["module"]
            record_id = args["record_id"]
            territory_id = args["territory_id"]

            result = await self.territories_client.assign_territory_to_record(
                module, record_id, territory_id
            )

            if result.get("data"):
                return f"Territory assigned to {module} {record_id}"

            return f"Failed to assign territory: {result}"

        except Exception as e:
            return f"Error: {str(e)}"

    # ========================================================================
    # ADVANCED: METADATA
    # ========================================================================

    async def _get_field_info(self, args: dict) -> str:
        try:
            module = args["module"]
            field_id = args.get("field_id")
            field_type = args.get("field_type", "all")

            result = await self.metadata_client.get_field_metadata(module, field_id, field_type)
            return self.metadata_client.format_field_summary(result)

        except Exception as e:
            logger.error(f"Error getting field info: {e}")
            return f"Error: {str(e)}"

    async def _update_field_settings(self, args: dict) -> str:
        try:
            module = args["module"]
            field_id = args["field_id"]
            updates_json = args["updates_json"]

            updates = json.loads(updates_json)

            result = await self.metadata_client.update_custom_field(module, field_id, updates)

            if result.get("fields"):
                return f"Field updated successfully!\nModule: {module}\nField ID: {field_id}"

            return f"Failed to update field: {result}"

        except Exception as e:
            logger.error(f"Error updating field: {e}")
            return f"Error: {str(e)}"

    async def _remove_custom_field(self, args: dict) -> str:
        try:
            module = args["module"]
            field_id = args["field_id"]

            result = await self.metadata_client.delete_custom_field(module, field_id)

            if result.get("fields") and result["fields"][0].get("code") == "SUCCESS":
                return f"Custom field deleted successfully!\nModule: {module}\nField ID: {field_id}"

            return f"Failed to delete field: {result}"

        except Exception as e:
            logger.error(f"Error deleting field: {e}")
            return f"Error: {str(e)}"

    async def _get_module_layouts(self, args: dict) -> str:
        try:
            module = args["module"]
            result = await self.metadata_client.get_layouts(module)
            return self.metadata_client.format_layout_summary(result)

        except Exception as e:
            logger.error(f"Error getting layouts: {e}")
            return f"Error: {str(e)}"

    async def _get_layout_details(self, args: dict) -> str:
        try:
            module = args["module"]
            layout_id = args["layout_id"]
            result = await self.metadata_client.get_layout_by_id(module, layout_id)
            return self.metadata_client.format_layout_summary(result)

        except Exception as e:
            logger.error(f"Error getting layout details: {e}")
            return f"Error: {str(e)}"

    async def _update_layout_configuration(self, args: dict) -> str:
        try:
            module = args["module"]
            layout_id = args["layout_id"]
            updates_json = args["updates_json"]

            updates = json.loads(updates_json)

            result = await self.metadata_client.update_custom_layout(module, layout_id, updates)

            if result.get("layouts"):
                return f"Layout updated successfully!\nModule: {module}\nLayout ID: {layout_id}"

            return f"Failed to update layout: {result}"

        except Exception as e:
            logger.error(f"Error updating layout: {e}")
            return f"Error: {str(e)}"

    async def _delete_layout(self, args: dict) -> str:
        try:
            module = args["module"]
            layout_id = args["layout_id"]
            transfer_to = args["transfer_to"]

            result = await self.metadata_client.delete_custom_layout(module, layout_id, transfer_to)

            if result.get("layouts"):
                return f"Layout deleted successfully!\nModule: {module}\nLayout ID: {layout_id}\nRecords transferred to: {transfer_to}"

            return f"Failed to delete layout: {result}"

        except Exception as e:
            logger.error(f"Error deleting layout: {e}")
            return f"Error: {str(e)}"

    async def _list_inventory_templates(self, args: dict) -> str:
        try:
            module = args.get("module")
            category = args.get("category")

            result = await self.metadata_client.get_inventory_templates(module, category)
            return self.metadata_client.format_template_summary(result)

        except Exception as e:
            logger.error(f"Error listing templates: {e}")
            return f"Error: {str(e)}"

    async def _get_template_details(self, args: dict) -> str:
        try:
            template_id = args["template_id"]
            result = await self.metadata_client.get_inventory_template_by_id(template_id)

            if result.get("inventory_templates"):
                template = result["inventory_templates"][0]
                output = "Template Details:\n\n"
                output += f"Name: {template.get('name', 'N/A')}\n"
                output += f"ID: {template.get('id', 'N/A')}\n"

                if template.get("module"):
                    output += f"Module: {template['module'].get('api_name', 'N/A')}\n"

                output += f"Category: {template.get('category', 'N/A')}\n"
                output += f"Editor Mode: {template.get('editor_mode', 'N/A')}\n"
                output += f"Favorite: {template.get('favorite', False)}\n"

                return output

            return "Template not found"

        except Exception as e:
            logger.error(f"Error getting template details: {e}")
            return f"Error: {str(e)}"

    async def _list_module_tags(self, args: dict) -> str:
        try:
            module = args["module"]
            my_tags_only = args.get("my_tags_only", False)

            result = await self.metadata_client.get_tags_list(module, my_tags_only)
            return self.metadata_client.format_tags_summary(result)

        except Exception as e:
            logger.error(f"Error listing tags: {e}")
            return f"Error: {str(e)}"

    async def _search_tags(self, args: dict) -> str:
        try:
            module = args["module"]
            tag_name_contains = args["tag_name_contains"]

            result = await self.metadata_client.get_tags_for_module(module)

            matching_tags = [
                tag for tag in result
                if tag_name_contains.lower() in tag.get("name", "").lower()
            ]

            if matching_tags:
                output = f"Found {len(matching_tags)} matching tag(s) for '{tag_name_contains}':\n\n"
                for tag in matching_tags:
                    output += f"- {tag.get('name', 'N/A')}\n"
                    output += f"  ID: {tag.get('id', 'N/A')}\n"
                    output += f"  Color: {tag.get('colour_code', 'N/A')}\n\n"
                return output

            return f"No tags found matching '{tag_name_contains}' in {module}"

        except Exception as e:
            logger.error(f"Error searching tags: {e}")
            return f"Error: {str(e)}"
