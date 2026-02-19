import json
import logging
import asyncio
import re
from typing import List, Dict, Any, Optional, Callable

import httpx

from config.prompts import get_system_prompt
from services.tool_service import ToolService
from services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class AgentService:
    """
    Core AI agent with a controlled agentic loop.

    Calls Claude Opus 4.1 via OpenRouter, executes tool calls via ToolService,
    and iterates until the LLM produces a final text response.
    This eliminates the n8n problem where the agent says "let me check"
    without actually executing tools.
    """

    def __init__(
        self,
        openrouter_api_key: str,
        openrouter_model: str,
        openrouter_base_url: str,
        tool_service: ToolService,
        memory_service: MemoryService,
        tool_definitions: List[Dict[str, Any]],
        max_tool_calls: int = 25,
        timeout_seconds: int = 120,
    ):
        self.api_key = openrouter_api_key
        self.model = openrouter_model
        self.base_url = openrouter_base_url
        self.tool_service = tool_service
        self.memory_service = memory_service
        self.tool_definitions = tool_definitions
        self.max_tool_calls = max_tool_calls
        self.timeout = timeout_seconds
        self.http_client = httpx.AsyncClient(timeout=float(timeout_seconds))

    async def process_message(
        self,
        user_id: int,
        user_message: str,
        on_thinking: Optional[Callable] = None,
    ) -> str:
        """
        Process a user message through the full agentic loop.

        Args:
            user_id: Telegram user ID
            user_message: The text message from the user
            on_thinking: Async callback to refresh "typing..." indicator

        Returns:
            Final text response from the LLM
        """
        try:
            # 1. Load conversation history
            history = await self.memory_service.get_history(user_id)

            # 2. Build messages array
            system_prompt = get_system_prompt()
            messages = history + [{"role": "user", "content": user_message}]

            # 3. Run the agentic loop
            response_text, new_messages = await self._agentic_loop(
                system_prompt=system_prompt,
                messages=messages,
                on_thinking=on_thinking,
            )

            # 4. Save new messages to Postgres (user message + all agent exchanges)
            messages_to_save = [{"role": "user", "content": user_message}]
            messages_to_save.extend(new_messages)
            await self.memory_service.save_messages(user_id, messages_to_save)

            return response_text

        except asyncio.TimeoutError:
            logger.error(f"Agent timeout for user {user_id}")
            return "The request took too long. Please try a simpler query."
        except Exception as e:
            logger.error(f"Agent error for user {user_id}: {e}", exc_info=True)
            return f"An error occurred: {str(e)}"

    async def _agentic_loop(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
        on_thinking: Optional[Callable] = None,
    ) -> tuple[str, List[Dict[str, Any]]]:
        """
        Run the agentic loop until the LLM produces a final text response.

        Returns:
            Tuple of (final_text, list_of_new_messages_generated_during_loop)
        """
        new_messages: List[Dict[str, Any]] = []
        pending_file_markers: List[str] = []
        iteration = 0

        while iteration < self.max_tool_calls:
            # Call OpenRouter
            response = await self._call_openrouter(system_prompt, messages)

            choice = response["choices"][0]
            finish_reason = choice.get("finish_reason", "")
            message = choice["message"]

            # Check if the LLM wants to call tools
            tool_calls = message.get("tool_calls")

            if tool_calls:
                # Append assistant message (with tool_calls) to conversation
                assistant_msg = {"role": "assistant", "content": message.get("content")}
                assistant_msg["tool_calls"] = tool_calls
                messages.append(assistant_msg)
                new_messages.append(assistant_msg)

                # Execute each tool call
                for tool_call in tool_calls:
                    tool_name = tool_call["function"]["name"]
                    try:
                        arguments = json.loads(tool_call["function"]["arguments"])
                    except json.JSONDecodeError:
                        arguments = {}

                    logger.info(f"Executing tool: {tool_name} with args: {arguments}")

                    # Execute the tool
                    result = await self.tool_service.execute_tool(tool_name, arguments)

                    # Capture [SEND_FILE:path] markers from tool results
                    # so we can append them to the final response (the LLM
                    # won't pass these through in its text output).
                    for match in re.finditer(r'\[SEND_FILE:.+?\]', result):
                        pending_file_markers.append(match.group(0))

                    # Append tool result to conversation
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result,
                    }
                    messages.append(tool_msg)
                    new_messages.append(tool_msg)

                    logger.info(f"Tool {tool_name} returned {len(result)} chars")

                # Refresh typing indicator
                if on_thinking:
                    try:
                        await on_thinking()
                    except Exception:
                        pass

                iteration += 1
            else:
                # Final text response - no more tool calls
                final_text = message.get("content", "")

                # Append any file markers captured from tool results
                if pending_file_markers:
                    final_text = final_text + "\n" + "\n".join(pending_file_markers)

                final_msg = {"role": "assistant", "content": final_text}
                new_messages.append(final_msg)
                return final_text, new_messages

        # Safety: max iterations reached
        final_text = (
            "I've reached the maximum number of tool calls for this request. "
            "Here's what I found so far. Please try a simpler query if you need more."
        )
        if pending_file_markers:
            final_text = final_text + "\n" + "\n".join(pending_file_markers)
        new_messages.append({"role": "assistant", "content": final_text})
        return final_text, new_messages

    async def _call_openrouter(
        self,
        system_prompt: str,
        messages: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """
        Make a single call to OpenRouter's chat completions API.
        """
        # Build the full messages list with system prompt
        api_messages = [{"role": "system", "content": system_prompt}] + messages

        payload = {
            "model": self.model,
            "messages": api_messages,
            "tools": self.tool_definitions,
            "tool_choice": "auto",
            "max_tokens": 4096,
            "temperature": 0.1,
        }

        response = await self.http_client.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://medicaltravel.co",
                "X-Title": "Medical Travel Colombia CRM Bot",
            },
            json=payload,
        )

        if response.status_code != 200:
            error_text = response.text
            logger.error(f"OpenRouter API error {response.status_code}: {error_text}")
            raise Exception(f"OpenRouter API error {response.status_code}: {error_text}")

        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.http_client.aclose()
