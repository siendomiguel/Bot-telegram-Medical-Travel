import io
import logging

import httpx

logger = logging.getLogger(__name__)


class VoiceService:
    """Transcribes voice messages using OpenAI Whisper API."""

    def __init__(self, openai_api_key: str):
        self.api_key = openai_api_key
        self.client = httpx.AsyncClient(timeout=30.0)

    async def transcribe(self, audio_bytes: bytes, language: str = "es") -> str:
        """
        Transcribe audio bytes using OpenAI Whisper API.

        Args:
            audio_bytes: Raw audio file bytes (OGG from Telegram)
            language: Language hint (default: Spanish for Medical Travel Colombia)

        Returns:
            Transcribed text
        """
        try:
            response = await self.client.post(
                "https://api.openai.com/v1/audio/transcriptions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                files={"file": ("voice.ogg", io.BytesIO(audio_bytes), "audio/ogg")},
                data={"model": "whisper-1", "language": language},
            )
            response.raise_for_status()
            result = response.json()
            return result.get("text", "")
        except httpx.HTTPStatusError as e:
            logger.error(f"Whisper API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Voice transcription failed: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Voice transcription error: {e}")
            raise

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()
