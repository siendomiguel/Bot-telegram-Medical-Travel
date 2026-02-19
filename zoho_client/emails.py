"""
Zoho CRM Email Integration
Send emails and manage email templates
Based on: https://www.zoho.com/crm/developer/docs/api/v8/send-mail.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoEmails:
    """Handle email operations in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def send_email(
        self,
        to_emails: List[str],
        from_email: str,
        subject: str,
        content: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        reply_to: Optional[str] = None,
        org_email: Optional[bool] = False
    ) -> Dict[str, Any]:
        """
        Send an email from Zoho CRM.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/send-mail.html

        Args:
            to_emails: List of recipient email addresses
            from_email: Sender email address (must be configured in Zoho CRM)
            subject: Email subject
            content: Email body (HTML supported)
            cc_emails: CC recipients
            bcc_emails: BCC recipients
            reply_to: Reply-to email address
            org_email: Send using organization email

        Returns:
            Send result from Zoho API
        """
        endpoint = "/crm/v8/actions/send_mail"

        data = {
            "data": [{
                "from": {"email": from_email},
                "to": [{"email": email} for email in to_emails],
                "subject": subject,
                "content": content,
                "org_email": org_email
            }]
        }

        if cc_emails:
            data["data"][0]["cc"] = [{"email": email} for email in cc_emails]

        if bcc_emails:
            data["data"][0]["bcc"] = [{"email": email} for email in bcc_emails]

        if reply_to:
            data["data"][0]["reply_to"] = {"email": reply_to}

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Email sent to: {', '.join(to_emails)}")
            return result

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise

    async def send_email_to_record(
        self,
        module: str,
        record_id: str,
        from_email: str,
        subject: str,
        content: str,
        cc_emails: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Send email to a specific record (Lead, Contact, etc.).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/send-mail.html

        Args:
            module: Module name (Leads, Contacts, etc.)
            record_id: Record ID to send email to
            from_email: Sender email
            subject: Email subject
            content: Email body
            cc_emails: CC recipients

        Returns:
            Send result
        """
        endpoint = f"/crm/v8/{module}/{record_id}/actions/send_mail"

        data = {
            "data": [{
                "from": {"email": from_email},
                "subject": subject,
                "content": content
            }]
        }

        if cc_emails:
            data["data"][0]["cc"] = [{"email": email} for email in cc_emails]

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Email sent to {module} record: {record_id}")
            return result

        except Exception as e:
            logger.error(f"Error sending email to record: {e}")
            raise

    async def get_email_templates(
        self,
        module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get email templates.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-email-templates.html

        Args:
            module: Filter templates by module

        Returns:
            List of email templates
        """
        endpoint = "/crm/v8/settings/email_templates"

        params = {}
        if module:
            params["module"] = module

        try:
            result = await self.client._request("GET", endpoint, params=params)
            return result

        except Exception as e:
            logger.error(f"Error getting email templates: {e}")
            raise

    async def send_email_with_template(
        self,
        module: str,
        record_id: str,
        template_id: str,
        from_email: str
    ) -> Dict[str, Any]:
        """
        Send email using a template.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/send-mail.html

        Args:
            module: Module name
            record_id: Record ID
            template_id: Email template ID
            from_email: Sender email

        Returns:
            Send result
        """
        endpoint = f"/crm/v8/{module}/{record_id}/actions/send_mail"

        data = {
            "data": [{
                "from": {"email": from_email},
                "template": {"id": template_id}
            }]
        }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Email sent with template {template_id} to {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error sending email with template: {e}")
            raise
