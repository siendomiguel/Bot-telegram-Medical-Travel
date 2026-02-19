"""
Zoho CRM Workflow Automation
Manage workflow rules and automation
Based on: https://www.zoho.com/crm/developer/docs/api/v8/workflow-rules.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoWorkflows:
    """Handle workflow automation in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def get_workflow_rules(
        self,
        module: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all workflow rules.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-workflow-rules.html

        Args:
            module: Filter by module name

        Returns:
            List of workflow rules
        """
        endpoint = "/crm/v8/settings/workflow_rules"

        params = {}
        if module:
            params["module"] = module

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info("Retrieved workflow rules")
            return result

        except Exception as e:
            logger.error(f"Error getting workflow rules: {e}")
            raise

    async def get_workflow_rule(
        self,
        rule_id: str
    ) -> Dict[str, Any]:
        """
        Get a specific workflow rule.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/get-workflow-rule.html

        Args:
            rule_id: Workflow rule ID

        Returns:
            Workflow rule details
        """
        endpoint = f"/crm/v8/settings/workflow_rules/{rule_id}"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info(f"Retrieved workflow rule: {rule_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting workflow rule: {e}")
            raise

    async def execute_workflow(
        self,
        module: str,
        record_id: str,
        workflow_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Execute specific workflow rules on a record.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/execute-workflow.html

        Args:
            module: Module name
            record_id: Record ID
            workflow_ids: List of workflow IDs to execute

        Returns:
            Execution result
        """
        endpoint = f"/crm/v8/{module}/{record_id}/actions/workflow"

        data = {
            "workflow": workflow_ids
        }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Executed {len(workflow_ids)} workflows on {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error executing workflow: {e}")
            raise
