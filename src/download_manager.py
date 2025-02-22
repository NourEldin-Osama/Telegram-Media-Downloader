import os
from functools import lru_cache
from typing import Optional, Tuple

from telethon import TelegramClient
from telethon.tl.types import (
    DocumentAttributeFilename,
    MessageMediaDocument,
    MessageMediaPhoto,
)

from FastTelethon import download_file
from config import settings


class DownloadManager:
    def __init__(self, client: TelegramClient):
        self.client = client
        self.total_downloads = 0
        self.skipped_files = 0
        self.filtered_files = 0
        self.output_dir = settings.OUTPUT_DIR
        self.allowed_formats = settings.ALLOWED_FORMATS
        self.download_all = settings.DOWNLOAD_ALL

        os.makedirs(self.output_dir, exist_ok=True)

    @lru_cache()
    def should_download_file(self, ext: str) -> bool:
        if self.download_all:
            return True
        return ext.lstrip(".").lower() in self.allowed_formats

    def get_file_extension(self, message) -> Optional[str]:
        if isinstance(message.media, MessageMediaPhoto):
            return ".jpg"
        elif isinstance(message.media, MessageMediaDocument):
            for attr in message.media.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    return f".{attr.file_name.split('.')[-1]}"

            # Fallback to mime type if available
            mime_type = getattr(message.media.document, "mime_type", "")
            if "image" in mime_type:
                return ".jpg"
            elif "audio" in mime_type:
                return ".mp3"
            elif "video" in mime_type:
                return ".mp4"
        return ".unknown"

    def get_file_name(self, message) -> str:
        """Get the original filename from a message"""
        if isinstance(message.media, MessageMediaDocument):
            for attr in message.media.document.attributes:
                if isinstance(attr, DocumentAttributeFilename):
                    return attr.file_name
        # Fallback to message ID with extension
        return f"{message.id}{self.get_file_extension(message)}"

    async def download_file(self, message) -> Tuple[bool, str]:
        if not message.media:
            return False, "No media in message"

        filename = self.get_file_name(message)
        if not filename:
            return False, "Could not determine filename"

        ext = os.path.splitext(filename)[1]
        if not self.should_download_file(ext):
            self.filtered_files += 1
            return False, f"File format '{ext}' not allowed for {filename}"

        filepath = os.path.join(str(self.output_dir), filename)
        if os.path.exists(filepath):
            self.skipped_files += 1
            return False, f"File already exists: {filepath}"

        try:
            with open(filepath, "wb") as file:
                await download_file(self.client, message.media.document, file)
            self.total_downloads += 1
            return True, filename
        except Exception as e:
            return False, f"Error downloading {filename}: {type(e).__name__} - {str(e)}"

    def get_stats(self) -> dict:
        return {
            "total_downloads": self.total_downloads,
            "skipped_files": self.skipped_files,
            "filtered_files": self.filtered_files,
        }
