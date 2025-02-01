import asyncio
import os
from functools import lru_cache
from typing import Optional

from FastTelethon import download_file
from telethon import TelegramClient
from telethon.tl.types import (
    DocumentAttributeFilename,
    MessageMediaDocument,
    MessageMediaPhoto,
)

from config import settings

# Get credentials from .env
API_ID = settings.API_ID
API_HASH = settings.API_HASH
PHONE_NUMBER = settings.PHONE_NUMBER
CHANNEL_USERNAME = settings.CHANNEL_USERNAME
ALLOWED_FORMATS = settings.ALLOWED_FORMATS
DOWNLOAD_ALL = settings.DOWNLOAD_ALL

# Validate environment variables
if not all([API_ID, API_HASH, PHONE_NUMBER, CHANNEL_USERNAME]):
    raise ValueError("Missing required environment variables")


def get_file_extension(message) -> Optional[str]:
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
        else:
            return ".unknown"
    return None


def get_file_name(message) -> str:
    """Get the original filename from a message"""
    if isinstance(message.media, MessageMediaDocument):
        for attr in message.media.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return attr.file_name
    # Fallback to message ID with extension
    return f"{message.id}{get_file_extension(message)}"


@lru_cache()
def should_download_file(ext: str) -> bool:
    if DOWNLOAD_ALL:
        return True
    return ext.lstrip(".").lower() in ALLOWED_FORMATS


async def main():
    os.makedirs(settings.OUTPUT_DIR, exist_ok=True)

    async with TelegramClient("session_name", int(API_ID), API_HASH) as client:
        await client.start(PHONE_NUMBER)

        if not await client.is_user_authorized():
            print("Authorization failed!")
            return

        channel = await client.get_entity(CHANNEL_USERNAME)
        print(f"Downloading media from: {channel.title}")
        print(
            f"Allowed formats: {'all' if DOWNLOAD_ALL else ', '.join(ALLOWED_FORMATS)}"
        )

        total, skipped, filtered = 0, 0, 0

        async for message in client.iter_messages(
            channel, limit=settings.HISTORY_LIMIT, reverse=settings.REVERSE_ORDER
        ):
            if not message.media:
                continue

            filename = get_file_name(message)
            if not filename:
                continue

            ext = os.path.splitext(filename)[1]
            if not should_download_file(ext):
                filtered += 1
                continue

            filepath = os.path.join(str(settings.OUTPUT_DIR), filename)

            if os.path.exists(filepath):
                skipped += 1
                continue

            try:
                with open(filepath, "wb") as file:
                    await download_file(client, message.media.document, file)
                print(f"Downloaded: {filename}")
                total += 1
            except Exception as e:
                print(f"Error downloading {filename}: {str(e)}")

        print(f"\nCompleted: {total} files downloaded")
        print(f"Skipped: {skipped} existing files")
        print(f"Filtered: {filtered} files (wrong format)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
