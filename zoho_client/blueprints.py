"""
Zoho CRM Blueprints (Process Management)
Manage blueprint transitions and processes
Based on: https://www.zoho.com/crm/developer/docs/api/v8/blueprint-api.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoBlueprints:
    """Handle blueprint processes in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def get_blueprint(
        self,
        module: str,
        record_id: str
    ) -> Dict[str, Any]:
        """
        Get blueprint details for a record.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-blueprint.html

        Args:
            module: Module name
            record_id: Record ID

        Returns:
            Blueprint details with available transitions
        """
        endpoint = f"/crm/v8/{module}/{record_id}/actions/blueprint"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info(f"Retrieved blueprint for {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting blueprint: {e}")
            raise

    async def update_blueprint(
        self,
        module: str,
        record_id: str,
        transition_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a blueprint transition.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/update-blueprint.html

        Args:
            module: Module name
            record_id: Record ID
            transition_id: Transition ID to execute
            data: Transition data (fields to update)

        Returns:
            Transition result
        """
        endpoint = f"/crm/v8/{module}/{record_id}/actions/blueprint"

        payload = {
            "blueprint": [{
                "transition_id": transition_id,
                "data": data
            }]
        }

        try:
            result = await self.client._request("PUT", endpoint, json=payload)
            logger.info(f"Executed blueprint transition {transition_id} on {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error updating blueprint: {e}")
            raise
