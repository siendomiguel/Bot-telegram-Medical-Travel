"""
Medical Travel Colombia - Zoho CRM Telegram Bot
Entry point: wires all services, controllers, and middleware together.

Run with: python app.py
"""

import sys
import os
import logging
import asyncio

# Add repo root to path so zoho_client/ is importable
sys.path.insert(0, os.path.dirname(__file__))

# Load .env into os.environ so zoho_client/ can read Zoho credentials
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config.settings import Settings
from controllers.command_controller import CommandController
from controllers.message_controller import MessageController
from controllers.voice_controller import VoiceController
from services.agent_service import AgentService
from services.memory_service import MemoryService
from services.voice_service import VoiceService
from services.tool_service import ToolService
from models.tool_schemas import TOOL_DEFINITIONS
from middleware.auth import AuthMiddleware
from middleware.error_handler import error_handler


def setup_logging(level: str) -> None:
    """Configure logging for the bot."""
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
    # Quiet noisy libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


async def main() -> None:
    """Initialize all services and start the bot."""
    # Load settings
    settings = Settings()
    setup_logging(settings.LOG_LEVEL)
    logger = logging.getLogger(__name__)

    logger.info("Starting Medical Travel Colombia CRM Bot...")
    logger.info(f"Model: {settings.OPENROUTER_MODEL}")
    logger.info(f"Allowed users: {len(settings.allowed_user_ids)}")
    logger.info(f"Tools available: {len(TOOL_DEFINITIONS)}")

    # Initialize services
    memory_service = MemoryService(
        database_url=settings.DATABASE_URL,
        max_turns=settings.MAX_CONVERSATION_TURNS,
    )
    await memory_service.initialize()
    logger.info("Memory service initialized (PostgreSQL)")

    tool_service = ToolService()
    logger.info(f"Tool service initialized ({len(tool_service._tool_map)} Zoho CRM tools)")

    voice_service = None
    if settings.OPENAI_API_KEY:
        voice_service = VoiceService(openai_api_key=settings.OPENAI_API_KEY)
        logger.info("Voice service initialized (Whisper)")
    else:
        logger.info("Voice service DISABLED (no OPENAI_API_KEY)")

    agent_service = AgentService(
        openrouter_api_key=settings.OPENROUTER_API_KEY,
        openrouter_model=settings.OPENROUTER_MODEL,
        openrouter_base_url=settings.OPENROUTER_BASE_URL,
        tool_service=tool_service,
        memory_service=memory_service,
        tool_definitions=TOOL_DEFINITIONS,
        max_tool_calls=settings.MAX_TOOL_CALLS_PER_TURN,
        timeout_seconds=settings.AGENT_TIMEOUT_SECONDS,
    )
    logger.info("Agent service initialized (agentic loop)")

    # Initialize controllers
    command_ctrl = CommandController(memory_service)
    message_ctrl = MessageController(agent_service)
    voice_ctrl = VoiceController(voice_service, agent_service) if voice_service else None

    # Auth middleware
    auth = AuthMiddleware(settings.allowed_user_ids)

    # Build Telegram application
    app = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", auth.require_auth(command_ctrl.start)))
    app.add_handler(CommandHandler("help", auth.require_auth(command_ctrl.help)))
    app.add_handler(CommandHandler("clear", auth.require_auth(command_ctrl.clear)))

    # Register message handlers
    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            auth.require_auth(message_ctrl.handle_message),
        )
    )
    if voice_ctrl:
        app.add_handler(
            MessageHandler(
                filters.VOICE | filters.AUDIO,
                auth.require_auth(voice_ctrl.handle_voice),
            )
        )

    # Global error handler
    app.add_error_handler(error_handler)

    # Start the bot
    logger.info("Bot is starting polling...")
    await app.initialize()
    await app.start()
    await app.updater.start_polling(drop_pending_updates=True)

    logger.info("Bot is running! Waiting for messages...")

    # Keep running until interrupted
    stop_event = asyncio.Event()

    def signal_handler():
        stop_event.set()

    try:
        loop = asyncio.get_event_loop()
        for sig_name in ("SIGINT", "SIGTERM"):
            try:
                import signal
                loop.add_signal_handler(getattr(signal, sig_name), signal_handler)
            except (AttributeError, NotImplementedError):
                # Windows doesn't support add_signal_handler
                pass

        await stop_event.wait()
    except (KeyboardInterrupt, SystemExit):
        pass
    finally:
        logger.info("Shutting down...")
        await app.updater.stop()
        await app.stop()
        await app.shutdown()
        await agent_service.close()
        if voice_service:
            await voice_service.close()
        await memory_service.close()
        logger.info("Bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
