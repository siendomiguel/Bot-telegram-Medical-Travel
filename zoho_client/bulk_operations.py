"""
Zoho CRM Bulk Operations
Handles:
1. Basic bulk operations (create, update, delete up to 100 records)
2. Bulk Read API - Export up to 200,000 records
3. Bulk Write API - Import up to 25,000 records
4. Backup API - Schedule and download CRM backups

Based on: https://www.zoho.com/crm/developer/docs/api/v8/bulk-apis.html
"""

import os
import logging
import asyncio
import httpx
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoBulkOperations:
    """Handle bulk operations in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def bulk_create(
        self,
        module: str,
        records: List[Dict[str, Any]],
        trigger_workflow: bool = False
    ) -> Dict[str, Any]:
        """
        Create multiple records at once (up to 100 per request).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/insert-records.html

        Args:
            module: Module name
            records: List of record data dictionaries (max 100)
            trigger_workflow: Whether to trigger workflow rules

        Returns:
            Bulk creation result
        """
        if len(records) > 100:
            raise ValueError("Maximum 100 records per bulk create operation")

        endpoint = f"/crm/v8/{module}"

        data = {
            "data": records,
            "trigger": ["workflow"] if trigger_workflow else []
        }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Bulk created {len(records)} records in {module}")
            return result

        except Exception as e:
            logger.error(f"Error in bulk create: {e}")
            raise

    async def bulk_update(
        self,
        module: str,
        records: List[Dict[str, Any]],
        trigger_workflow: bool = False
    ) -> Dict[str, Any]:
        """
        Update multiple records at once (up to 100 per request).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/update-records.html

        Args:
            module: Module name
            records: List of records with 'id' field (max 100)
            trigger_workflow: Whether to trigger workflow rules

        Returns:
            Bulk update result
        """
        if len(records) > 100:
            raise ValueError("Maximum 100 records per bulk update operation")

        endpoint = f"/crm/v8/{module}"

        data = {
            "data": records,
            "trigger": ["workflow"] if trigger_workflow else []
        }

        try:
            result = await self.client._request("PUT", endpoint, json=data)
            logger.info(f"Bulk updated {len(records)} records in {module}")
            return result

        except Exception as e:
            logger.error(f"Error in bulk update: {e}")
            raise

    async def bulk_upsert(
        self,
        module: str,
        records: List[Dict[str, Any]],
        duplicate_check_fields: List[str],
        trigger_workflow: bool = False
    ) -> Dict[str, Any]:
        """
        Bulk upsert (create or update) records.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/upsert-records.html

        Args:
            module: Module name
            records: List of record data (max 100)
            duplicate_check_fields: Fields to check for duplicates
            trigger_workflow: Whether to trigger workflow rules

        Returns:
            Bulk upsert result
        """
        if len(records) > 100:
            raise ValueError("Maximum 100 records per bulk upsert operation")

        endpoint = f"/crm/v8/{module}/upsert"

        data = {
            "data": records,
            "duplicate_check_fields": duplicate_check_fields,
            "trigger": ["workflow"] if trigger_workflow else []
        }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Bulk upserted {len(records)} records in {module}")
            return result

        except Exception as e:
            logger.error(f"Error in bulk upsert: {e}")
            raise

    async def bulk_delete(
        self,
        module: str,
        record_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Delete multiple records at once (up to 100 per request).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/delete-records.html

        Args:
            module: Module name
            record_ids: List of record IDs to delete (max 100)

        Returns:
            Bulk deletion result
        """
        if len(record_ids) > 100:
            raise ValueError("Maximum 100 records per bulk delete operation")

        endpoint = f"/crm/v8/{module}"

        params = {
            "ids": ",".join(record_ids)
        }

        try:
            result = await self.client._request("DELETE", endpoint, params=params)
            logger.info(f"Bulk deleted {len(record_ids)} records from {module}")
            return result

        except Exception as e:
            logger.error(f"Error in bulk delete: {e}")
            raise

    async def mass_update(
        self,
        module: str,
        cvid: str,
        field_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Mass update records matching a custom view criteria.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/mass-update.html

        Args:
            module: Module name
            cvid: Custom View ID (filter criteria)
            field_updates: Fields to update

        Returns:
            Mass update job details
        """
        endpoint = f"/crm/v8/{module}/actions/mass_update"

        data = {
            "cvid": cvid,
            "data": [field_updates]
        }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Mass update initiated for {module}")
            return result

        except Exception as e:
            logger.error(f"Error in mass update: {e}")
            raise

    async def mass_delete(
        self,
        module: str,
        cvid: str
    ) -> Dict[str, Any]:
        """
        Mass delete records matching a custom view criteria.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/mass-delete.html

        Args:
            module: Module name
            cvid: Custom View ID (filter criteria)

        Returns:
            Mass delete job details
        """
        endpoint = f"/crm/v8/{module}/actions/mass_delete"

        data = {
            "cvid": cvid
        }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Mass delete initiated for {module}")
            return result

        except Exception as e:
            logger.error(f"Error in mass delete: {e}")
            raise

    async def check_mass_operation_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a mass operation job.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/mass-operations-status.html

        Args:
            job_id: Job ID from mass operation

        Returns:
            Job status details
        """
        endpoint = f"/crm/v8/actions/mass_operations/{job_id}"

        try:
            result = await self.client._request("GET", endpoint)
            return result

        except Exception as e:
            logger.error(f"Error checking job status: {e}")
            raise

    # ============================================================================
    # BULK READ API - Export large datasets (up to 200,000 records)
    # ============================================================================

    async def create_bulk_read_job(
        self,
        module: str,
        fields: Optional[List[str]] = None,
        criteria: Optional[str] = None,
        cvid: Optional[str] = None,
        page: int = 1,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a bulk read job to export records from Zoho CRM.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-read.html

        Args:
            module: Module API name (e.g., "Leads", "Contacts")
            fields: List of field API names to export (optional - all fields if not specified)
            criteria: Filter criteria (e.g., "(Email:equals:test@example.com)")
            cvid: Custom view ID to apply filters
            page: Page number (default 1, max 200,000 records per job)
            callback_url: URL to receive notification when job completes

        Returns:
            Job details including job_id, state, and created_time

        OAuth Scopes Required:
            - ZohoCRM.bulk.read
            - ZohoCRM.modules.{module_name}.READ
        """
        endpoint = "/crm/bulk/v8/read"

        query = {
            "module": {"api_name": module}
        }

        if fields:
            query["fields"] = fields

        if criteria:
            query["criteria"] = criteria

        if cvid:
            query["cvid"] = cvid

        if page > 1:
            query["page"] = page

        data: Dict[str, Any] = {"query": query}

        if callback_url:
            data["callback"] = {
                "url": callback_url,
                "method": "post"
            }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Bulk read job created for {module}: {result.get('details', {}).get('id')}")
            return result

        except Exception as e:
            logger.error(f"Error creating bulk read job: {e}")
            raise

    async def get_bulk_read_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a bulk read job.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-read.html#get-status

        Args:
            job_id: Job ID from create_bulk_read_job

        Returns:
            Job status with details including:
            - state: ADDED, QUEUED, IN PROGRESS, COMPLETED
            - operation: read
            - result: Download URL when COMPLETED

        OAuth Scopes Required:
            - ZohoCRM.bulk.read
        """
        endpoint = f"/crm/bulk/v8/read/{job_id}"

        try:
            result = await self.client._request("GET", endpoint)
            return result

        except Exception as e:
            logger.error(f"Error getting bulk read status: {e}")
            raise

    async def download_bulk_read_result(
        self,
        job_id: str,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download the result of a completed bulk read job.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-read.html#download

        Args:
            job_id: Job ID from bulk read job
            save_path: Optional path to save the downloaded ZIP file

        Returns:
            Dict with download info or file path if saved

        OAuth Scopes Required:
            - ZohoCRM.bulk.read

        Note:
            - Maximum 10 download requests per minute
            - Result is a ZIP file containing CSV
            - CSV includes "id" column by default
        """
        endpoint = f"/crm/bulk/v8/read/{job_id}/result"

        try:
            # Get download URL from status
            status = await self.get_bulk_read_status(job_id)

            if status.get("state") != "COMPLETED":
                return {
                    "status": "pending",
                    "message": f"Job not completed yet. Current state: {status.get('state')}",
                    "job_status": status
                }

            # Get download URL
            download_url = status.get("result", {}).get("download_url")
            if not download_url:
                raise ValueError("No download URL found in completed job")

            # Download the file
            token = await self.client.auth.get_access_token()
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}

            async with httpx.AsyncClient(timeout=60.0) as http_client:
                response = await http_client.get(download_url, headers=headers)
                response.raise_for_status()

                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Downloaded bulk read result to {save_path}")
                    return {
                        "status": "success",
                        "message": "File downloaded successfully",
                        "file_path": save_path,
                        "size_bytes": len(response.content)
                    }
                else:
                    return {
                        "status": "success",
                        "message": "Data retrieved successfully",
                        "size_bytes": len(response.content),
                        "data": response.content
                    }

        except Exception as e:
            logger.error(f"Error downloading bulk read result: {e}")
            raise

    async def bulk_export_module(
        self,
        module: str,
        fields: Optional[List[str]] = None,
        criteria: Optional[str] = None,
        save_path: Optional[str] = None,
        max_wait_seconds: int = 300,
        poll_interval: int = 5
    ) -> Dict[str, Any]:
        """
        Complete workflow: Create bulk export job, poll status, and download results.

        This is a convenience method that combines:
        1. create_bulk_read_job()
        2. Polling get_bulk_read_status() until COMPLETED
        3. download_bulk_read_result()

        Args:
            module: Module API name
            fields: Optional list of fields to export
            criteria: Optional filter criteria
            save_path: Optional path to save ZIP file
            max_wait_seconds: Maximum time to wait for job completion (default 300)
            poll_interval: Seconds between status checks (default 5)

        Returns:
            Dict with job details and download info

        OAuth Scopes Required:
            - ZohoCRM.bulk.read
            - ZohoCRM.modules.{module_name}.READ
        """
        try:
            # Step 1: Create job
            logger.info(f"Creating bulk export job for {module}...")
            job_result = await self.create_bulk_read_job(
                module=module,
                fields=fields,
                criteria=criteria
            )

            job_id = job_result.get("details", {}).get("id")
            if not job_id:
                raise ValueError("No job ID returned from bulk read job creation")

            logger.info(f"Job created: {job_id}. Polling for completion...")

            # Step 2: Poll for completion
            elapsed = 0
            while elapsed < max_wait_seconds:
                status = await self.get_bulk_read_status(job_id)
                state = status.get("state")

                logger.debug(f"Job {job_id} state: {state}")

                if state == "COMPLETED":
                    logger.info(f"Job {job_id} completed successfully")
                    break
                elif state in ["ADDED", "QUEUED", "IN PROGRESS"]:
                    await asyncio.sleep(poll_interval)
                    elapsed += poll_interval
                else:
                    raise ValueError(f"Job failed with state: {state}")

            if elapsed >= max_wait_seconds:
                return {
                    "status": "timeout",
                    "message": f"Job did not complete within {max_wait_seconds} seconds",
                    "job_id": job_id,
                    "last_state": state
                }

            # Step 3: Download results
            logger.info(f"Downloading results for job {job_id}...")
            download_result = await self.download_bulk_read_result(job_id, save_path)

            return {
                "status": "success",
                "message": "Bulk export completed successfully",
                "job_id": job_id,
                "module": module,
                "download": download_result
            }

        except Exception as e:
            logger.error(f"Error in bulk export workflow: {e}")
            raise

    # ============================================================================
    # BULK WRITE API - Import large datasets (up to 25,000 records)
    # ============================================================================

    async def upload_bulk_write_file(
        self,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Upload a ZIP file containing CSV for bulk write operation.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-write.html#upload

        Args:
            file_path: Path to ZIP file (must contain CSV with field API names in first row)

        Returns:
            Dict with file_id for use in create_bulk_write_job

        OAuth Scopes Required:
            - ZohoFiles.files.ALL

        Notes:
            - Maximum 25,000 records per CSV
            - Maximum file size: 25MB
            - CSV first row must contain field API names
            - File must be compressed in ZIP format
        """
        upload_url = "https://content.zohoapis.com/crm/v8/upload"

        try:
            token = await self.client.auth.get_access_token()
            zgid = os.getenv("ZOHO_ORG_ID", "")

            headers = {
                "Authorization": f"Zoho-oauthtoken {token}",
                "feature": "bulk-write",
                "X-CRM-ORG": zgid
            }

            async with httpx.AsyncClient(timeout=60.0) as http_client:
                with open(file_path, "rb") as f:
                    files = {"file": f}
                    response = await http_client.post(
                        upload_url,
                        headers=headers,
                        files=files
                    )
                    response.raise_for_status()
                    result = response.json()

            logger.info(f"Uploaded file: {result.get('details', {}).get('file_id')}")
            return result

        except Exception as e:
            logger.error(f"Error uploading bulk write file: {e}")
            raise

    async def create_bulk_write_job(
        self,
        file_id: str,
        operation: str,
        module: str,
        field_mappings: List[Dict[str, Any]],
        find_by: Optional[str] = None,
        callback_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a bulk write job to import records.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-write.html

        Args:
            file_id: File ID from upload_bulk_write_file
            operation: "insert", "update", or "upsert"
            module: Module API name (e.g., "Leads")
            field_mappings: List of field mappings, e.g.:
                [{"api_name": "Last_Name", "index": 0}, {"api_name": "Email", "index": 1}]
            find_by: Field to use for upsert duplicate checking (required for upsert)
            callback_url: URL to receive notification when job completes

        Returns:
            Job details including job ID

        OAuth Scopes Required:
            - ZohoCRM.bulk.CREATE
            - ZohoCRM.bulk.ALL
            - ZohoCRM.modules.ALL

        Notes:
            - Maximum 25,000 records per operation
            - Separate CSV files required for parent/child modules
        """
        endpoint = "/crm/bulk/v8/write"

        resource = {
            "type": "data",
            "module": {"api_name": module},
            "file_id": file_id,
            "field_mappings": field_mappings
        }

        if find_by:
            resource["find_by"] = find_by

        data: Dict[str, Any] = {
            "operation": operation,
            "resource": [resource]
        }

        if callback_url:
            data["callback"] = {
                "url": callback_url,
                "method": "post"
            }

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Bulk write job created: {result.get('details', {}).get('id')}")
            return result

        except Exception as e:
            logger.error(f"Error creating bulk write job: {e}")
            raise

    async def get_bulk_write_status(
        self,
        job_id: str
    ) -> Dict[str, Any]:
        """
        Check the status of a bulk write job.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-write.html#get-status

        Args:
            job_id: Job ID from create_bulk_write_job

        Returns:
            Job status with details including:
            - status: ADDED, IN PROGRESS, COMPLETED
            - operation: insert, update, or upsert
            - file: Statistics (added_count, skipped_count, updated_count, total_count)

        OAuth Scopes Required:
            - ZohoCRM.bulk.CREATE
            - ZohoCRM.bulk.ALL
        """
        endpoint = f"/crm/bulk/v8/write/{job_id}"

        try:
            result = await self.client._request("GET", endpoint)
            return result

        except Exception as e:
            logger.error(f"Error getting bulk write status: {e}")
            raise

    async def download_bulk_write_result(
        self,
        job_id: str,
        save_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Download the result CSV of a bulk write job (includes errors).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/bulk-write.html#download

        Args:
            job_id: Job ID from bulk write job
            save_path: Optional path to save the result CSV

        Returns:
            Dict with download info or file path if saved

        OAuth Scopes Required:
            - ZohoCRM.bulk.CREATE
            - ZohoCRM.bulk.ALL

        Note:
            CSV contains:
            - First three mapped columns from uploaded file
            - STATUS: added/skipped/updated/unprocessed
            - RECORD_ID: Added/updated record's ID
            - ERRORS: Error codes with details
        """
        try:
            # Get job status
            status = await self.get_bulk_write_status(job_id)

            job_status = status.get("data", [{}])[0].get("status")
            if job_status != "COMPLETED":
                return {
                    "status": "pending",
                    "message": f"Job not completed yet. Current status: {job_status}",
                    "job_status": status
                }

            # Get download URL
            download_url = status.get("data", [{}])[0].get("result", {}).get("download_url")
            if not download_url:
                raise ValueError("No download URL found in completed job")

            # Download the file
            token = await self.client.auth.get_access_token()
            headers = {"Authorization": f"Zoho-oauthtoken {token}"}

            async with httpx.AsyncClient(timeout=60.0) as http_client:
                response = await http_client.get(download_url, headers=headers)
                response.raise_for_status()

                if save_path:
                    with open(save_path, "wb") as f:
                        f.write(response.content)
                    logger.info(f"Downloaded bulk write result to {save_path}")
                    return {
                        "status": "success",
                        "message": "File downloaded successfully",
                        "file_path": save_path,
                        "size_bytes": len(response.content)
                    }
                else:
                    return {
                        "status": "success",
                        "message": "Data retrieved successfully",
                        "size_bytes": len(response.content),
                        "data": response.content
                    }

        except Exception as e:
            logger.error(f"Error downloading bulk write result: {e}")
            raise

    # ============================================================================
    # BACKUP API - Schedule and manage CRM backups
    # ============================================================================

    async def schedule_data_backup(
        self,
        rrule: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule an immediate or recurring data backup.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/backup.html

        Args:
            rrule: Recurrence rule for scheduled backups (optional - empty for immediate backup)
                Examples:
                - "RRULE:FREQ=WEEKLY;INTERVAL=2;BYDAY=TU" - Every 2 weeks on Tuesday
                - "RRULE:FREQ=MONTHLY;INTERVAL=1;BYMONTHDAY=15" - 15th of every month
                - None or empty dict for immediate one-time backup

        Returns:
            Backup job details including job ID

        OAuth Scopes Required:
            - ZohoCRM.bulk.backup.ALL
            - ZohoCRM.bulk.backup.CREATE

        Notes:
            - FREQ: WEEKLY or MONTHLY
            - INTERVAL: 1-52 (frequency gap)
            - BYDAY: SU, MO, TU, WE, TH, FR, SA
            - BYMONTHDAY: 1-31
        """
        endpoint = "/crm/bulk/v8/backup"

        data: Dict[str, Any] = {}

        if rrule:
            data["backup"] = {"rrule": rrule}

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Backup scheduled: {result.get('backup', {}).get('details', {}).get('id')}")
            return result

        except Exception as e:
            logger.error(f"Error scheduling backup: {e}")
            raise

    async def get_backup_info(self) -> Dict[str, Any]:
        """
        Get current backup schedule information.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/backup.html#get-info

        Returns:
            Backup schedule details including:
            - id: Backup identifier
            - scheduled_date: Next backup time (ISO 8601)
            - start_date: Initial scheduling time
            - rrule: Recurrence rule
            - requester: User who scheduled
            - status: STOPPED, SCHEDULED, INPROGRESS, COMPLETED, FAILED

        OAuth Scopes Required:
            - ZohoCRM.bulk.backup.ALL
            - ZohoCRM.bulk.backup.READ
        """
        endpoint = "/crm/bulk/v8/backup"

        try:
            result = await self.client._request("GET", endpoint)
            return result

        except Exception as e:
            logger.error(f"Error getting backup info: {e}")
            raise

    async def get_backup_history(
        self,
        page: int = 1,
        per_page: int = 200
    ) -> Dict[str, Any]:
        """
        Get backup history (past one year).

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/backup.html#history

        Args:
            page: Page number (default 1)
            per_page: Records per page (default/max 200)

        Returns:
            Array of past backup jobs with:
            - id: Backup job ID
            - done_by: User who scheduled
            - log_time: Backup scheduling timestamp
            - state: Completion status
            - action: Backup action type
            - repeat_type: Backup frequency
            - file_name: Backup file name
            - count: Additional backup count

        OAuth Scopes Required:
            - ZohoCRM.bulk.backup.ALL
            - ZohoCRM.bulk.backup.READ

        Note:
            - Returns 204 status if no backups found
            - History limited to past one year
        """
        endpoint = "/crm/bulk/v8/backup/history"

        params = {
            "page": page,
            "per_page": per_page
        }

        try:
            result = await self.client._request("GET", endpoint, params=params)
            return result

        except Exception as e:
            logger.error(f"Error getting backup history: {e}")
            raise

    async def download_backup(
        self,
        job_id: str,
        save_directory: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get backup download URLs and optionally download files.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/backup.html#download

        Args:
            job_id: Backup job ID from history
            save_directory: Optional directory to save backup files

        Returns:
            Dict with download URLs and file info

        OAuth Scopes Required:
            - ZohoFiles.files.ALL

        Note:
            - Maximum file size is 1GB
            - Multiple files generated if data exceeds 1GB
            - Returns 204 status if no download links available
        """
        endpoint = "/crm/bulk/v8/backup/urls"

        params = {"job_id": job_id}

        try:
            result = await self.client._request("GET", endpoint, params=params)

            urls = result.get("urls", {})
            data_links = urls.get("data_links", [])
            attachment_links = urls.get("attachment_links", [])
            expiry_date = urls.get("expiry_date")

            if save_directory and (data_links or attachment_links):
                os.makedirs(save_directory, exist_ok=True)

                token = await self.client.auth.get_access_token()
                headers = {"Authorization": f"Zoho-oauthtoken {token}"}

                downloaded_files = []

                async with httpx.AsyncClient(timeout=120.0) as http_client:
                    # Download data files
                    for idx, url in enumerate(data_links):
                        file_path = os.path.join(save_directory, f"Data_{idx:03d}.zip")
                        response = await http_client.get(url, headers=headers)
                        response.raise_for_status()
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        downloaded_files.append(file_path)
                        logger.info(f"Downloaded data file: {file_path}")

                    # Download attachment files
                    for idx, url in enumerate(attachment_links):
                        file_path = os.path.join(save_directory, f"Attachments_{idx:03d}.zip")
                        response = await http_client.get(url, headers=headers)
                        response.raise_for_status()
                        with open(file_path, "wb") as f:
                            f.write(response.content)
                        downloaded_files.append(file_path)
                        logger.info(f"Downloaded attachment file: {file_path}")

                return {
                    "status": "success",
                    "message": "Backup files downloaded successfully",
                    "downloaded_files": downloaded_files,
                    "expiry_date": expiry_date
                }

            return {
                "status": "success",
                "data_links": data_links,
                "attachment_links": attachment_links,
                "expiry_date": expiry_date,
                "message": "Use data_links and attachment_links to download files"
            }

        except Exception as e:
            logger.error(f"Error downloading backup: {e}")
            raise

    async def cancel_backup(
        self,
        backup_id: str
    ) -> Dict[str, Any]:
        """
        Cancel a scheduled backup.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/backup.html#cancel

        Args:
            backup_id: Backup schedule ID from get_backup_info

        Returns:
            Cancellation confirmation

        OAuth Scopes Required:
            - ZohoCRM.bulk.backup.ALL
            - ZohoCRM.bulk.backup.UPDATE
        """
        endpoint = f"/crm/bulk/v8/backup/{backup_id}/actions/cancel"

        try:
            result = await self.client._request("PUT", endpoint)
            logger.info(f"Backup {backup_id} cancelled")
            return result

        except Exception as e:
            logger.error(f"Error cancelling backup: {e}")
            raise
