"""
Zoho CRM Territory Management
Manage territories and assignments
Based on: https://www.zoho.com/crm/developer/docs/api/v8/territories-api.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoTerritories:
    """Handle territory management in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def get_territories(self) -> Dict[str, Any]:
        """
        Get all territories.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-territories.html

        Returns:
            List of all territories
        """
        endpoint = "/crm/v8/settings/territories"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info("Retrieved territories")
            return result

        except Exception as e:
            logger.error(f"Error getting territories: {e}")
            raise

    async def get_territory(
        self,
        territory_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific territory.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-territory.html

        Args:
            territory_id: Territory ID

        Returns:
            Territory details
        """
        endpoint = f"/crm/v8/settings/territories/{territory_id}"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info(f"Retrieved territory: {territory_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting territory: {e}")
            raise

    async def assign_territory_to_record(
        self,
        module: str,
        record_id: str,
        territory_id: str
    ) -> Dict[str, Any]:
        """
        Assign a territory to a record.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/update-records.html

        Args:
            module: Module name
            record_id: Record ID
            territory_id: Territory ID to assign

        Returns:
            Assignment result
        """
        endpoint = f"/crm/v8/{module}/{record_id}"

        data = {
            "data": [{
                "id": record_id,
                "Territory": {"id": territory_id}
            }]
        }

        try:
            result = await self.client._request("PUT", endpoint, json=data)
            logger.info(f"Assigned territory {territory_id} to {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error assigning territory: {e}")
            raise
