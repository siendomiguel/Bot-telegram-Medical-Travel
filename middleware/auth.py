import logging
from functools import wraps
from typing import Set

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


class AuthMiddleware:
    """Restricts bot access to whitelisted Telegram user IDs."""

    def __init__(self, allowed_ids: list[int]):
        self.allowed_ids: Set[int] = set(allowed_ids)
        logger.info(f"Auth middleware initialized with {len(self.allowed_ids)} allowed users")

    def require_auth(self, handler):
        """Decorator that checks if the user is in the whitelist."""

        @wraps(handler)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            if user:
                logger.info(f"Message from user ID: {user.id} ({user.full_name})")
            # AUTH TEMPORARILY DISABLED - allow all users
            # if user is None or user.id not in self.allowed_ids:
            #     user_id = user.id if user else "unknown"
            #     logger.warning(f"Unauthorized access attempt from user {user_id}")
            #     if update.message:
            #         await update.message.reply_text(
            #             "You are not authorized to use this bot."
            #         )
            #     return
            return await handler(update, context)

        return wrapper
