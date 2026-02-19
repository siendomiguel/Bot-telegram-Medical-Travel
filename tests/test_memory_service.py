import pytest
import json
from unittest.mock import AsyncMock, MagicMock, patch


class TestMemoryService:
    """Test memory service with mocked asyncpg."""

    @pytest.fixture
    def memory_service(self):
        """Create a MemoryService with a mocked connection pool."""
        with patch("services.memory_service.asyncpg") as mock_asyncpg:
            from services.memory_service import MemoryService
            service = MemoryService(
                database_url="postgresql://test:test@localhost:5432/test",
                max_turns=50,
            )
            # Mock the pool
            service.pool = AsyncMock()
            yield service

    @pytest.mark.asyncio
    async def test_save_messages(self, memory_service):
        """Test saving messages to the database."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]

        await memory_service.save_messages(user_id=123, messages=messages)
        assert memory_service.pool.executemany.called or memory_service.pool.execute.called

    @pytest.mark.asyncio
    async def test_get_history_returns_list(self, memory_service):
        """Test that get_history returns a list of message dicts."""
        # Mock the fetch result
        mock_rows = [
            {
                "role": "user",
                "content": "Find leads",
                "tool_calls": None,
                "tool_call_id": None,
            },
            {
                "role": "assistant",
                "content": "Here are your leads...",
                "tool_calls": None,
                "tool_call_id": None,
            },
        ]
        memory_service.pool.fetch.return_value = mock_rows

        history = await memory_service.get_history(user_id=123)
        assert isinstance(history, list)
        memory_service.pool.fetch.assert_called_once()

    @pytest.mark.asyncio
    async def test_clear_history(self, memory_service):
        """Test clearing conversation history."""
        await memory_service.clear_history(user_id=123)
        memory_service.pool.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_cleanup_old(self, memory_service):
        """Test cleaning up old conversations."""
        await memory_service.cleanup_old(days=30)
        memory_service.pool.execute.assert_called_once()
