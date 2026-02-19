import pytest
from unittest.mock import AsyncMock, patch, MagicMock


class TestToolService:
    """Test tool dispatch without hitting real Zoho API."""

    @pytest.fixture
    def tool_service(self):
        """Create a ToolService with mocked zoho_client instances."""
        with patch("services.tool_service.ZohoModules") as MockModules, \
             patch("services.tool_service.ZohoActivities") as MockActivities, \
             patch("services.tool_service.ZohoNotes") as MockNotes, \
             patch("services.tool_service.ZohoSearch") as MockSearch, \
             patch("services.tool_service.ZohoFiles") as MockFiles, \
             patch("services.tool_service.ZohoEmails") as MockEmails, \
             patch("services.tool_service.ZohoBulkOperations") as MockBulk, \
             patch("services.tool_service.ZohoCustomModules") as MockCustom, \
             patch("services.tool_service.ZohoWorkflows") as MockWorkflows, \
             patch("services.tool_service.ZohoBlueprints") as MockBlueprints, \
             patch("services.tool_service.ZohoPriceBooks") as MockPriceBooks, \
             patch("services.tool_service.ZohoWebForms") as MockWebForms, \
             patch("services.tool_service.ZohoTerritories") as MockTerritories, \
             patch("services.tool_service.ZohoMetadata") as MockMetadata, \
             patch("services.tool_service.ZohoAdvancedOperations") as MockAdvanced, \
             patch("services.tool_service.ZohoCOQL") as MockCOQL:

            from services.tool_service import ToolService
            service = ToolService()

            # Replace clients with async mocks
            service.modules_client = AsyncMock()
            service.activities_client = AsyncMock()
            service.notes_client = AsyncMock()
            service.search_client = AsyncMock()
            service.files_client = AsyncMock()
            service.emails_client = AsyncMock()
            service.bulk_client = AsyncMock()
            service.custom_modules_client = AsyncMock()
            service.workflows_client = AsyncMock()
            service.blueprints_client = AsyncMock()
            service.pricebooks_client = AsyncMock()
            service.webforms_client = AsyncMock()
            service.territories_client = AsyncMock()

            yield service

    @pytest.mark.asyncio
    async def test_create_lead_success(self, tool_service):
        """Test successful lead creation."""
        tool_service.modules_client.create_record.return_value = {
            "data": [{"code": "SUCCESS", "details": {"id": "123456"}}]
        }
        result = await tool_service.execute_tool("create_lead", {
            "last_name": "Smith",
            "company": "Acme Inc",
        })
        assert "123456" in result
        tool_service.modules_client.create_record.assert_called_once()

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self, tool_service):
        """Test that an unknown tool name returns an error string."""
        result = await tool_service.execute_tool("nonexistent_tool", {})
        assert "Unknown tool" in result

    @pytest.mark.asyncio
    async def test_search_leads(self, tool_service):
        """Test lead search dispatches correctly."""
        tool_service.search_client.format_search_results.return_value = "Found 2 leads"
        tool_service.search_client.search_by_conditions.return_value = {"data": []}

        result = await tool_service.execute_tool("search_leads", {
            "company": "Acme",
        })
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_tool_error_returns_error_string(self, tool_service):
        """Test that tool errors return a formatted error string."""
        tool_service.modules_client.create_record.side_effect = Exception("API timeout")
        result = await tool_service.execute_tool("create_lead", {
            "last_name": "Smith",
            "company": "Acme",
        })
        assert "Error" in result or "error" in result

    @pytest.mark.asyncio
    async def test_health_check(self, tool_service):
        """Test health check tool."""
        tool_service.modules_client.health_check.return_value = True
        result = await tool_service.execute_tool("zoho_health_check", {})
        assert "healthy" in result.lower() or "accessible" in result.lower()
