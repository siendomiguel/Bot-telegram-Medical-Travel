import logging
import asyncio
import os
import re

from telegram import Update
from telegram.ext import ContextTypes

from services.agent_service import AgentService
from utils.formatting import clean_for_telegram, split_text

logger = logging.getLogger(__name__)


class MessageController:
    """Handles incoming text messages from Telegram."""

    def __init__(self, agent_service: AgentService):
        self.agent_service = agent_service

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Process a text message through the AI agent."""
        user_message = update.message.text
        user = update.effective_user
        user_id = user.id

        logger.info(f"[TEXT] from user {user_id} ({user.full_name}): {user_message[:200]}")

        # Start a background task that sends "typing..." every 4 seconds
        typing_task = asyncio.create_task(
            self._keep_typing(update.message.chat)
        )

        try:
            # Process through the agentic loop
            response = await self.agent_service.process_message(
                user_id=user_id,
                user_message=user_message,
                on_thinking=None,
            )
        finally:
            # Stop the typing indicator
            typing_task.cancel()
            try:
                await typing_task
            except asyncio.CancelledError:
                pass

        # Clean and send response
        await self._send_response(update, response)

    async def _keep_typing(self, chat) -> None:
        """Continuously send 'typing...' action every 4 seconds until cancelled."""
        try:
            while True:
                await chat.send_action("typing")
                await asyncio.sleep(4)
        except asyncio.CancelledError:
            pass
        except Exception:
            pass

    async def _send_response(self, update: Update, text: str) -> None:
        """Send response to Telegram, splitting if necessary. Handles [SEND_FILE:path] markers."""
        # Check for file markers
        file_path = None
        file_match = re.search(r'\[SEND_FILE:(.+?)\]', text)
        if file_match:
            file_path = file_match.group(1)
            text = text.replace(file_match.group(0), "").strip()

        text = clean_for_telegram(text)
        chunks = split_text(text, max_length=4096)

        for chunk in chunks:
            try:
                await update.message.reply_text(chunk)
            except Exception as e:
                logger.error(f"Failed to send message chunk: {e}")
                try:
                    await update.message.reply_text(chunk)
                except Exception:
                    await update.message.reply_text(
                        "I generated a response but couldn't send it. "
                        "Please try again with a simpler query."
                    )
                    break

        # Send file if marker was found
        if file_path and os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    await update.message.reply_document(
                        document=f,
                        filename=os.path.basename(file_path),
                    )
                logger.info(f"Sent file: {file_path}")
            except Exception as e:
                logger.error(f"Failed to send file {file_path}: {e}")
                await update.message.reply_text("Sorry, I couldn't send the PDF file.")
            finally:
                try:
                    os.remove(file_path)
                    logger.info(f"Cleaned up temp file: {file_path}")
                except OSError:
                    pass
