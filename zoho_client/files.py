"""
Zoho CRM File Management
Handles file uploads, downloads, and attachments
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoFiles:
    """Handle file operations in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def upload_file(
        self,
        module: str,
        record_id: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        Upload a file attachment to a record.

        Args:
            module: Module name (e.g., "Leads", "Contacts")
            record_id: The record ID to attach file to
            file_path: Full path to the file to upload

        Returns:
            Upload result from Zoho API
        """
        endpoint = f"/crm/v8/{module}/{record_id}/Attachments"

        try:
            import os
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read file
            with open(file_path, 'rb') as f:
                file_data = f.read()

            file_name = os.path.basename(file_path)

            # Prepare multipart form data
            files = {
                'file': (file_name, file_data)
            }

            result = await self.client._request(
                "POST",
                endpoint,
                files=files
            )

            logger.info(f"File uploaded successfully: {file_name} to {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            raise

    async def upload_photo(
        self,
        module: str,
        record_id: str,
        photo_path: str
    ) -> Dict[str, Any]:
        """
        Upload a photo to a record (for Contacts, Leads, etc.).

        Args:
            module: Module name
            record_id: Record ID
            photo_path: Path to photo file

        Returns:
            Upload result
        """
        endpoint = f"/crm/v8/{module}/{record_id}/photo"

        try:
            import os
            if not os.path.exists(photo_path):
                raise FileNotFoundError(f"Photo not found: {photo_path}")

            with open(photo_path, 'rb') as f:
                photo_data = f.read()

            files = {
                'photo': (os.path.basename(photo_path), photo_data)
            }

            result = await self.client._request(
                "POST",
                endpoint,
                files=files
            )

            logger.info(f"Photo uploaded to {module}:{record_id}")
            return result

        except Exception as e:
            logger.error(f"Error uploading photo: {e}")
            raise

    async def download_file(
        self,
        module: str,
        record_id: str,
        attachment_id: str,
        save_path: str
    ) -> str:
        """
        Download a file attachment from a record.

        Args:
            module: Module name
            record_id: Record ID
            attachment_id: Attachment ID
            save_path: Path where to save the file

        Returns:
            Path to downloaded file
        """
        endpoint = f"/crm/v8/{module}/{record_id}/Attachments/{attachment_id}"

        try:
            result = await self.client._request("GET", endpoint)

            # Save file
            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(result)

            logger.info(f"File downloaded to: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"Error downloading file: {e}")
            raise

    async def get_attachments(
        self,
        module: str,
        record_id: str
    ) -> Dict[str, Any]:
        """
        Get list of all attachments for a record.

        Args:
            module: Module name
            record_id: Record ID

        Returns:
            List of attachments
        """
        endpoint = f"/crm/v8/{module}/{record_id}/Attachments"

        try:
            result = await self.client._request("GET", endpoint)
            return result

        except Exception as e:
            logger.error(f"Error getting attachments: {e}")
            raise

    async def delete_attachment(
        self,
        module: str,
        record_id: str,
        attachment_id: str
    ) -> Dict[str, Any]:
        """
        Delete an attachment from a record.

        Args:
            module: Module name
            record_id: Record ID
            attachment_id: Attachment ID to delete

        Returns:
            Deletion result
        """
        endpoint = f"/crm/v8/{module}/{record_id}/Attachments/{attachment_id}"

        try:
            result = await self.client._request("DELETE", endpoint)
            logger.info(f"Attachment deleted: {attachment_id}")
            return result

        except Exception as e:
            logger.error(f"Error deleting attachment: {e}")
            raise

    async def download_photo(
        self,
        module: str,
        record_id: str,
        save_path: str
    ) -> str:
        """
        Download the photo of a record.

        Args:
            module: Module name
            record_id: Record ID
            save_path: Where to save the photo

        Returns:
            Path to saved photo
        """
        endpoint = f"/crm/v8/{module}/{record_id}/photo"

        try:
            result = await self.client._request("GET", endpoint)

            import os
            os.makedirs(os.path.dirname(save_path), exist_ok=True)

            with open(save_path, 'wb') as f:
                f.write(result)

            logger.info(f"Photo downloaded to: {save_path}")
            return save_path

        except Exception as e:
            logger.error(f"Error downloading photo: {e}")
            raise
