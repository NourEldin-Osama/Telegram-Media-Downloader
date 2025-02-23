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
    OUTPUT_BASE_DIR: str = (
        ""  # Base directory for downloads, empty means use PROJECT_ROOT
    )
    MAX_RETRIES: int = 3  # Number of retries for failed downloads
    DEBUG: bool = False  # Enable debug mode
    HISTORY_LIMIT: int = 100  # Number of messages to retrieve
    REVERSE_ORDER: bool = False  # Get messages in reverse order False=newest to oldest, True=oldest to newest

    @property
    def OUTPUT_DIR(self) -> Path:
        """Get the output directory path for downloaded media"""
        base_dir = Path(self.OUTPUT_BASE_DIR) if self.OUTPUT_BASE_DIR else PROJECT_ROOT
        return base_dir / f"{self.CHANNEL_USERNAME}_media"

    model_config = SettingsConfigDict(
        env_file=str(PROJECT_ROOT / ".env"), env_ignore_empty=True, extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
