"""
Zoho CRM Price Books
Manage price books and pricing
Based on: https://www.zoho.com/crm/developer/docs/api/v8/price-books-api.html
"""

import logging
from typing import Optional, Dict, Any, List
from .base_client import ZohoBaseClient

logger = logging.getLogger(__name__)


class ZohoPriceBooks:
    """Handle price books in Zoho CRM"""

    def __init__(self):
        self.client = ZohoBaseClient()

    async def create_price_book(
        self,
        pricing_name: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new price book.

        API Reference: https://www.zoho.com/crm/developer/docs/api/v8/insert-records.html

        Args:
            pricing_name: Price book name
            description: Price book description

        Returns:
            Created price book details
        """
        endpoint = "/crm/v8/Price_Books"

        data = {
            "data": [{
                "Pricing_Details__s": pricing_name
            }]
        }

        if description:
            data["data"][0]["Description"] = description

        try:
            result = await self.client._request("POST", endpoint, json=data)
            logger.info(f"Created price book: {pricing_name}")
            return result

        except Exception as e:
            logger.error(f"Error creating price book: {e}")
            raise

    async def get_price_book(
        self,
        price_book_id: str
    ) -> Dict[str, Any]:
        """
        Get a price book by ID.

        Args:
            price_book_id: Price book ID

        Returns:
            Price book details
        """
        endpoint = f"/crm/v8/Price_Books/{price_book_id}"

        try:
            result = await self.client._request("GET", endpoint)
            logger.info(f"Retrieved price book: {price_book_id}")
            return result

        except Exception as e:
            logger.error(f"Error getting price book: {e}")
            raise

    async def get_price_books(
        self,
        page: int = 1,
        per_page: int = 200
    ) -> Dict[str, Any]:
        """
        Get all price books.

        Args:
            page: Page number
            per_page: Records per page

        Returns:
            List of price books
        """
        endpoint = "/crm/v8/Price_Books"

        params = {
            "page": page,
            "per_page": per_page
        }

        try:
            result = await self.client._request("GET", endpoint, params=params)
            logger.info("Retrieved price books")
            return result

        except Exception as e:
            logger.error(f"Error getting price books: {e}")
            raise

    async def update_price_book(
        self,
        price_book_id: str,
        pricing_name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update a price book.

        Args:
            price_book_id: Price book ID
            pricing_name: New price book name
            description: New description

        Returns:
            Update result
        """
        endpoint = f"/crm/v8/Price_Books/{price_book_id}"

        data = {"data": [{"id": price_book_id}]}

        if pricing_name:
            data["data"][0]["Pricing_Details__s"] = pricing_name
        if description:
            data["data"][0]["Description"] = description

        try:
            result = await self.client._request("PUT", endpoint, json=data)
            logger.info(f"Updated price book: {price_book_id}")
            return result

        except Exception as e:
            logger.error(f"Error updating price book: {e}")
            raise

    async def delete_price_book(
        self,
        price_book_id: str
    ) -> Dict[str, Any]:
        """
        Delete a price book.

        Args:
            price_book_id: Price book ID

        Returns:
            Deletion result
        """
        endpoint = f"/crm/v8/Price_Books/{price_book_id}"

        try:
            result = await self.client._request("DELETE", endpoint)
            logger.info(f"Deleted price book: {price_book_id}")
            return result

        except Exception as e:
            logger.error(f"Error deleting price book: {e}")
            raise
