import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from services.agent_service import AgentService


class TestAgentService:
    """Test the agentic loop with mocked OpenRouter responses."""

    @pytest.fixture
    def mock_services(self):
        """Create mocked dependencies."""
        tool_service = AsyncMock()
        memory_service = AsyncMock()
        memory_service.get_history.return_value = []
        return tool_service, memory_service

    @pytest.fixture
    def agent(self, mock_services):
        """Create an AgentService with mocked dependencies."""
        tool_service, memory_service = mock_services
        return AgentService(
            openrouter_api_key="test-key",
            openrouter_model="test-model",
            openrouter_base_url="https://test.example.com/api/v1",
            tool_service=tool_service,
            memory_service=memory_service,
            tool_definitions=[],
            max_tool_calls=5,
            timeout_seconds=30,
        )

    @pytest.mark.asyncio
    async def test_simple_text_response(self, agent, mock_services):
        """LLM returns text without tool calls."""
        tool_service, memory_service = mock_services

        with patch.object(agent, "_call_openrouter") as mock_call:
            mock_call.return_value = {
                "choices": [{
                    "finish_reason": "stop",
                    "message": {
                        "content": "Hello! How can I help you?",
                    }
                }]
            }

            result = await agent.process_message(
                user_id=123,
                user_message="Hi",
            )

            assert "Hello" in result
            memory_service.save_messages.assert_called_once()
            # No tools should have been called
            tool_service.execute_tool.assert_not_called()

    @pytest.mark.asyncio
    async def test_single_tool_call(self, agent, mock_services):
        """LLM calls one tool, gets result, returns final text."""
        tool_service, memory_service = mock_services
        tool_service.execute_tool.return_value = "Found lead: John Smith (ID: 123)"

        call_count = 0

        async def mock_openrouter(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                # First call: LLM wants to use a tool
                return {
                    "choices": [{
                        "finish_reason": "tool_calls",
                        "message": {
                            "content": None,
                            "tool_calls": [{
                                "id": "call_1",
                                "function": {
                                    "name": "search_by_word",
                                    "arguments": json.dumps({
                                        "module": "Leads",
                                        "word": "John Smith"
                                    })
                                }
                            }]
                        }
                    }]
                }
            else:
                # Second call: LLM returns final text
                return {
                    "choices": [{
                        "finish_reason": "stop",
                        "message": {
                            "content": "I found John Smith in your leads."
                        }
                    }]
                }

        with patch.object(agent, "_call_openrouter", side_effect=mock_openrouter):
            result = await agent.process_message(
                user_id=123,
                user_message="Find John Smith",
            )

            assert "John Smith" in result
            tool_service.execute_tool.assert_called_once_with(
                "search_by_word",
                {"module": "Leads", "word": "John Smith"}
            )

    @pytest.mark.asyncio
    async def test_max_iterations_safety(self, agent, mock_services):
        """Loop stops after max_tool_calls iterations."""
        tool_service, memory_service = mock_services
        tool_service.execute_tool.return_value = "Some result"

        # Always return tool calls (infinite loop scenario)
        with patch.object(agent, "_call_openrouter") as mock_call:
            mock_call.return_value = {
                "choices": [{
                    "finish_reason": "tool_calls",
                    "message": {
                        "content": None,
                        "tool_calls": [{
                            "id": "call_loop",
                            "function": {
                                "name": "search_leads",
                                "arguments": "{}"
                            }
                        }]
                    }
                }]
            }

            result = await agent.process_message(
                user_id=123,
                user_message="Do something complex",
            )

            # Should have hit the safety limit
            assert "maximum" in result.lower()
            assert tool_service.execute_tool.call_count == agent.max_tool_calls

    @pytest.mark.asyncio
    async def test_tool_error_recovery(self, agent, mock_services):
        """Tool fails, error is passed back to LLM as tool result."""
        tool_service, memory_service = mock_services
        tool_service.execute_tool.return_value = "Tool error (search_leads): API timeout"

        call_count = 0

        async def mock_openrouter(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {
                    "choices": [{
                        "finish_reason": "tool_calls",
                        "message": {
                            "content": None,
                            "tool_calls": [{
                                "id": "call_err",
                                "function": {
                                    "name": "search_leads",
                                    "arguments": "{}"
                                }
                            }]
                        }
                    }]
                }
            else:
                return {
                    "choices": [{
                        "finish_reason": "stop",
                        "message": {
                            "content": "The search encountered an error. Please try again."
                        }
                    }]
                }

        with patch.object(agent, "_call_openrouter", side_effect=mock_openrouter):
            result = await agent.process_message(
                user_id=123,
                user_message="Search leads",
            )

            assert "error" in result.lower()
