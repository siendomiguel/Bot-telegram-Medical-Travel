"""
Zoho CRM Custom Modules and Metadata
Discover and work with custom modules
Based on: https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoCustomModules:
    """Handle custom modules and metadata in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def get_all_modules(self) -> Dict[str, Any]:
        """
        Get list of all modules (standard + custom).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html

        Returns:
            List of all modules with metadata
        """
        endpoint = "/crm/v8/settings/modules"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info("Retrieved all modules")
            return result

        except Exception as e:
            logger.error(f"Error getting modules: {e}")
            raise

    async def get_module_metadata(
        self,
        module: str
    ) -> Dict[str, Any]:
        """
        Get metadata for a specific module.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/modules-api.html

        Args:
            module: Module API name

        Returns:
            Module metadata including fields, layouts, etc.
        """
        endpoint = f"/crm/v8/settings/modules/{module}"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info(f"Retrieved metadata for {module}")
            return result

        except Exception as e:
            logger.error(f"Error getting module metadata: {e}")
            raise

    async def get_module_fields(
        self,
        module: str
    ) -> Dict[str, Any]:
        """
        Get all fields for a module.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/field-meta.html

        Args:
            module: Module API name

        Returns:
            List of all fields in the module
        """
        endpoint = f"/crm/v8/settings/fields"

        params = {"module": module}

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info(f"Retrieved fields for {module}")
            return result

        except Exception as e:
            logger.error(f"Error getting module fields: {e}")
            raise

    async def get_custom_views(
        self,
        module: str
    ) -> Dict[str, Any]:
        """
        Get custom views (filters) for a module.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/custom-views.html

        Args:
            module: Module API name

        Returns:
            List of custom views
        """
        endpoint = f"/crm/v8/settings/custom_views"

        params = {"module": module}

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info(f"Retrieved custom views for {module}")
            return result

        except Exception as e:
            logger.error(f"Error getting custom views: {e}")
            raise

    async def get_records_by_custom_view(
        self,
        module: str,
        cvid: str,
        page: int = 1,
        per_page: int = 200
    ) -> Dict[str, Any]:
        """
        Get records filtered by a custom view.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-records.html

        Args:
            module: Module API name
            cvid: Custom View ID
            page: Page number
            per_page: Records per page (max 200)

        Returns:
            Filtered records
        """
        endpoint = f"/crm/v8/{module}"

        params = {
            "cvid": cvid,
            "page": page,
            "per_page": per_page
        }

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info(f"Retrieved records from {module} using custom view {cvid}")
            return result

        except Exception as e:
            logger.error(f"Error getting records by custom view: {e}")
            raise

    async def get_related_lists(
        self,
        module: str
    ) -> Dict[str, Any]:
        """
        Get related lists for a module.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-related-list.html

        Args:
            module: Module API name

        Returns:
            List of related modules
        """
        endpoint = f"/crm/v8/settings/related_lists"

        params = {"module": module}

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info(f"Retrieved related lists for {module}")
            return result

        except Exception as e:
            logger.error(f"Error getting related lists: {e}")
            raise

    async def get_related_records(
        self,
        module: str,
        record_id: str,
        related_module: str,
        page: int = 1,
        per_page: int = 200
    ) -> Dict[str, Any]:
        """
        Get related records for a specific record.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-related-records.html

        Args:
            module: Parent module
            record_id: Parent record ID
            related_module: Related module name
            page: Page number
            per_page: Records per page

        Returns:
            Related records
        """
        endpoint = f"/crm/v8/{module}/{record_id}/{related_module}"

        params = {
            "page": page,
            "per_page": per_page
        }

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info(f"Retrieved {related_module} related to {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting related records: {e}")
            raise
