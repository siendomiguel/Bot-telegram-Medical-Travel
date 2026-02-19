import logging

from telegram import Update
from telegram.ext import ContextTypes

from services.memory_service import MemoryService

logger = logging.getLogger(__name__)


class CommandController:
    """Handles Telegram bot commands: /start, /help, /clear."""

    def __init__(self, memory_service: MemoryService):
        self.memory_service = memory_service

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user = update.effective_user
        logger.info(f"[/start] from user {user.id} ({user.full_name})")
        await update.message.reply_text(
            f"Welcome {user.first_name}! I'm the Medical Travel Colombia CRM Bot.\n\n"
            "I can help you manage your Zoho CRM:\n"
            "- Search for leads, contacts, deals\n"
            "- Create and update records\n"
            "- Manage tasks, events, and calls\n"
            "- Run reports and bulk operations\n\n"
            "Just type your request in natural language, or send a voice message.\n\n"
            "Commands:\n"
            "/start - Show this message\n"
            "/help - Show available features\n"
            "/clear - Clear conversation history"
        )

    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        user = update.effective_user
        logger.info(f"[/help] from user {user.id} ({user.full_name})")
        await update.message.reply_text(
            "Available Features:\n\n"
            "CRM Modules:\n"
            "- Leads, Contacts, Accounts, Deals\n"
            "- Products, Vendors, Quotes\n"
            "- Sales Orders, Purchase Orders, Invoices\n\n"
            "Activities:\n"
            "- Tasks, Events, Calls, Notes\n\n"
            "Search:\n"
            "- Search by name, email, phone\n"
            "- Advanced COQL queries\n"
            "- Bulk operations\n\n"
            "Examples:\n"
            '- "Find Maria Garcia"\n'
            '- "Create a lead for John Doe at Acme Inc"\n'
            '- "Show tasks due this week"\n'
            '- "Update lead status to Qualified"\n\n'
            "Tips:\n"
            "- I understand both English and Spanish\n"
            "- Send voice messages - I'll transcribe them\n"
            "- Use /clear to reset our conversation"
        )

    async def clear(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /clear command - clears conversation history."""
        user = update.effective_user
        logger.info(f"[/clear] from user {user.id} ({user.full_name})")
        await self.memory_service.clear_history(user.id)
        logger.info(f"Cleared history for user {user.id}")
        await update.message.reply_text("Conversation history cleared. Let's start fresh!")
