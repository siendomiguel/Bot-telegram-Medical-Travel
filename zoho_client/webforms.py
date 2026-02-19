"""
Zoho CRM Web Forms
Manage web forms and submissions
Based on: https://www.zoho.com/crm/developer/docs/api/v8/webforms.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoWebForms:
    """Handle web forms in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def get_webforms(
        self,
        module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all web forms.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-webforms.html

        Args:
            module: Filter by module

        Returns:
            List of web forms
        """
        endpoint = "/crm/v8/settings/webforms"

        params = {}
        if module:
            params["module"] = module

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info("Retrieved web forms")
            return result

        except Exception as e:
            logger.error(f"Error getting web forms: {e}")
            raise

    async def get_webform(
        self,
        webform_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific web form.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-webform.html

        Args:
            webform_id: Web form ID

        Returns:
            Web form details
        """
        endpoint = f"/crm/v8/settings/webforms/{webform_id}"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info(f"Retrieved web form: {webform_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting web form: {e}")
            raise
