"""Pydantic models for Telegram bot conversation memory."""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ConversationMessage(BaseModel):
    """A single turn in a conversation.

    Covers all three message roles used by the OpenRouter / OpenAI
    chat-completions API:

    * **user** -- ``content`` is the user's text.
    * **assistant** -- ``content`` and/or ``tool_calls``.
    * **tool** -- ``content`` is the tool result; ``tool_call_id`` links
      it back to the originating tool call.
    """

    role: str  # user, assistant, tool
    content: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class ConversationContext(BaseModel):
    """A snapshot of the conversation state for a single Telegram user."""

    user_id: int
    messages: List[ConversationMessage]
    created_at: datetime = datetime.utcnow()
