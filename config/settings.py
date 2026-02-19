import os
from typing import List, Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Telegram
    TELEGRAM_BOT_TOKEN: str
    ALLOWED_TELEGRAM_IDS: str  # comma-separated: "123,456,789,..."

    # OpenRouter (Claude Opus 4.1)
    OPENROUTER_API_KEY: str
    OPENROUTER_MODEL: str = "anthropic/claude-opus-4.1"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # OpenAI (Whisper) - optional, voice messages disabled if not set
    OPENAI_API_KEY: Optional[str] = None

    # PostgreSQL
    DATABASE_URL: str  # postgresql://user:pass@host:5432/dbname

    # Zoho CRM (shared with MCP server)
    ZOHO_CLIENT_ID: str
    ZOHO_CLIENT_SECRET: str
    ZOHO_REFRESH_TOKEN: str
    ZOHO_API_DOMAIN: str = "https://www.zohoapis.com"
    ZOHO_ACCOUNTS_DOMAIN: str = "https://accounts.zoho.com"

    # App config
    LOG_LEVEL: str = "INFO"
    MAX_CONVERSATION_TURNS: int = 50
    MAX_TOOL_CALLS_PER_TURN: int = 25
    AGENT_TIMEOUT_SECONDS: int = 120

    @property
    def allowed_user_ids(self) -> List[int]:
        return [int(uid.strip()) for uid in self.ALLOWED_TELEGRAM_IDS.split(",") if uid.strip()]

    model_config = {"env_file": os.path.join(os.path.dirname(__file__), "..", ".env")}
