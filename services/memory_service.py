"""
Memory service for Telegram bot conversation history.

Uses asyncpg for async PostgreSQL access. Stores per-user conversation
turns (user, assistant, tool) and retrieves them in chronological order
formatted for the OpenRouter chat-completions API.
"""

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

import asyncpg

logger = logging.getLogger(__name__)


class MemoryService:
    """Async PostgreSQL-backed conversation memory."""

    def __init__(self, database_url: str, max_turns: int = 50) -> None:
        """Store config; the connection pool is created lazily in initialize().

        Args:
            database_url: PostgreSQL DSN, e.g. ``postgresql://user:pass@host/db``.
            max_turns: Maximum number of recent messages to return per user.
        """
        self.database_url = database_url
        self.max_turns = max_turns
        self.pool: Optional[asyncpg.Pool] = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def initialize(self) -> None:
        """Create the asyncpg connection pool and ensure the schema exists."""
        self.pool = await asyncpg.create_pool(self.database_url)
        logger.info("asyncpg connection pool created")

        async with self.pool.acquire() as conn:
            await conn.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id              SERIAL PRIMARY KEY,
                    telegram_user_id BIGINT       NOT NULL,
                    role            VARCHAR(20)  NOT NULL,
                    content         TEXT,
                    tool_calls      JSONB,
                    tool_call_id    VARCHAR(100),
                    created_at      TIMESTAMPTZ  DEFAULT NOW()
                );
                """
            )
            # Speed up per-user lookups and age-based cleanup.
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversations_user_id
                    ON conversations (telegram_user_id);
                """
            )
            await conn.execute(
                """
                CREATE INDEX IF NOT EXISTS idx_conversations_created_at
                    ON conversations (created_at);
                """
            )
        logger.info("conversations table and indexes ensured")

    async def close(self) -> None:
        """Close the connection pool."""
        if self.pool is not None:
            await self.pool.close()
            self.pool = None
            logger.info("asyncpg connection pool closed")

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def get_history(self, user_id: int) -> list[dict[str, Any]]:
        """Load the last *max_turns* messages for *user_id*.

        Returns a list of dicts formatted for the OpenRouter / OpenAI
        chat-completions API::

            {"role": "user",      "content": "..."}
            {"role": "assistant", "content": "...", "tool_calls": [...]}
            {"role": "tool",      "tool_call_id": "...", "content": "..."}
        """
        assert self.pool is not None, "MemoryService not initialized"

        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT role, content, tool_calls, tool_call_id
                FROM conversations
                WHERE telegram_user_id = $1
                ORDER BY id DESC
                LIMIT $2
                """,
                user_id,
                self.max_turns,
            )

        # Rows come back newest-first; reverse to chronological order.
        rows = list(reversed(rows))

        messages: list[dict[str, Any]] = []
        for row in rows:
            msg: dict[str, Any] = {"role": row["role"]}

            if row["role"] == "assistant":
                if row["content"] is not None:
                    msg["content"] = row["content"]
                if row["tool_calls"] is not None:
                    # asyncpg returns JSONB as Python objects already.
                    tool_calls = row["tool_calls"]
                    if isinstance(tool_calls, str):
                        tool_calls = json.loads(tool_calls)
                    msg["tool_calls"] = tool_calls
            elif row["role"] == "tool":
                msg["content"] = row["content"] or ""
                if row["tool_call_id"] is not None:
                    msg["tool_call_id"] = row["tool_call_id"]
            else:
                # user (or any other role)
                msg["content"] = row["content"] or ""

            messages.append(msg)

        return messages

    async def save_messages(self, user_id: int, messages: list[dict[str, Any]]) -> None:
        """Persist a batch of messages for *user_id*.

        Each dict should contain at minimum ``role`` and ``content``.
        Optional keys: ``tool_calls`` (list), ``tool_call_id`` (str).
        """
        assert self.pool is not None, "MemoryService not initialized"

        if not messages:
            return

        async with self.pool.acquire() as conn:
            # Use a prepared statement inside a transaction for efficiency.
            async with conn.transaction():
                stmt = await conn.prepare(
                    """
                    INSERT INTO conversations
                        (telegram_user_id, role, content, tool_calls, tool_call_id)
                    VALUES ($1, $2, $3, $4::jsonb, $5)
                    """
                )
                for msg in messages:
                    tool_calls_json: Optional[str] = None
                    if msg.get("tool_calls") is not None:
                        tool_calls_json = json.dumps(msg["tool_calls"])

                    await stmt.fetchval(
                        user_id,
                        msg["role"],
                        msg.get("content"),
                        tool_calls_json,
                        msg.get("tool_call_id"),
                    )

        logger.debug("Saved %d message(s) for user %s", len(messages), user_id)

    async def clear_history(self, user_id: int) -> None:
        """Delete all stored messages for *user_id*."""
        assert self.pool is not None, "MemoryService not initialized"

        async with self.pool.acquire() as conn:
            await conn.execute(
                "DELETE FROM conversations WHERE telegram_user_id = $1",
                user_id,
            )
        logger.info("Cleared conversation history for user %s", user_id)

    async def cleanup_old(self, days: int = 30) -> None:
        """Delete messages older than *days* days."""
        assert self.pool is not None, "MemoryService not initialized"

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        async with self.pool.acquire() as conn:
            result = await conn.execute(
                "DELETE FROM conversations WHERE created_at < $1",
                cutoff,
            )
        logger.info("Cleaned up old messages (older than %d days): %s", days, result)
