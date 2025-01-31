from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.resolve()


class Settings(BaseSettings):
    API_ID: int
    API_HASH: str
    PHONE_NUMBER: str
    CHANNEL_USERNAME: str
    ALLOWED_FORMATS: list[str] = [
        "mp3",  # MPEG Audio Layer III
        "wav",  # Waveform Audio File Format
        "m4a",  # MPEG-4 Audio
        "ogg",  # Ogg Vorbis Audio
        "aac",  # Advanced Audio Coding
        "wma",  # Windows Media Audio
        "flac",  # Free Lossless Audio Codec
        "aiff",  # Audio Interchange File Format
        "alac",  # Apple Lossless Audio Codec
        "opus",  # Opus Audio Format
    ]  # Default audio formats
    DOWNLOAD_ALL: bool = False  # Default to False to only download specified formats

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"), env_ignore_empty=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
