import logging
import traceback

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Global error handler for the Telegram bot."""
    logger.error(f"Exception while handling an update: {context.error}")
    logger.error(traceback.format_exc())

    if isinstance(update, Update) and update.message:
        try:
            await update.message.reply_text(
                "An error occurred while processing your request. "
                "Please try again or use /clear to reset the conversation."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")
