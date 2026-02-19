import logging
import asyncio
import os
import re

from telegram import Update
from telegram.ext import ContextTypes

from services.agent_service import AgentService
from services.voice_service import VoiceService
from utils.formatting import clean_for_telegram, split_text

logger = logging.getLogger(__name__)


class VoiceController:
    """Handles voice messages: transcribe then process as text."""

    def __init__(self, voice_service: VoiceService, agent_service: AgentService):
        self.voice_service = voice_service
        self.agent_service = agent_service

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Download, transcribe, and process a voice message."""
        user = update.effective_user
        user_id = user.id

        logger.info(f"[VOICE] from user {user_id} ({user.full_name}), duration: {getattr(update.message.voice, 'duration', '?')}s")

        # Send typing indicator
        await update.message.chat.send_action("typing")

        # Get the voice or audio file
        voice = update.message.voice or update.message.audio
        if not voice:
            await update.message.reply_text("Could not process the audio file.")
            return

        try:
            # Download the voice file
            file = await context.bot.get_file(voice.file_id)
            voice_bytes = await file.download_as_bytearray()

            # Transcribe with Whisper
            transcription = await self.voice_service.transcribe(bytes(voice_bytes))

            if not transcription.strip():
                await update.message.reply_text("I couldn't understand the audio. Please try again.")
                return

            # Show what was heard
            await update.message.reply_text(f"I heard: {transcription}")

            # Start continuous typing indicator
            typing_task = asyncio.create_task(
                self._keep_typing(update.message.chat)
            )

            try:
                # Process transcription through the agent
                response = await self.agent_service.process_message(
                    user_id=user_id,
                    user_message=transcription,
                    on_thinking=None,
                )
            finally:
                typing_task.cancel()
                try:
                    await typing_task
                except asyncio.CancelledError:
                    pass

            # Send response (with file marker detection)
            file_path = None
            file_match = re.search(r'\[SEND_FILE:(.+?)\]', response)
            if file_match:
                file_path = file_match.group(1)
                response = response.replace(file_match.group(0), "").strip()

            text = clean_for_telegram(response)
            chunks = split_text(text, max_length=4096)
            for chunk in chunks:
                await update.message.reply_text(chunk)

            # Send file if marker was found
            if file_path and os.path.exists(file_path):
                try:
                    with open(file_path, "rb") as f:
                        await update.message.reply_document(
                            document=f,
                            filename=os.path.basename(file_path),
                        )
                    logger.info(f"Sent file via voice: {file_path}")
                except Exception as file_err:
                    logger.error(f"Failed to send file {file_path}: {file_err}")
                    await update.message.reply_text("Sorry, I couldn't send the PDF file.")
                finally:
                    try:
                        os.remove(file_path)
                    except OSError:
                        pass

        except Exception as e:
            logger.error(f"Voice processing error for user {user_id}: {e}", exc_info=True)
            await update.message.reply_text(
                "An error occurred while processing your voice message. "
                "Please try sending a text message instead."
            )

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
