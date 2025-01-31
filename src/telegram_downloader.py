import asyncio
import os

from telethon import TelegramClient
from telethon.tl.types import MessageMediaDocument, MessageMediaPhoto

from config import settings

# Get credentials from .env
API_ID = settings.API_ID
API_HASH = settings.API_HASH
PHONE_NUMBER = settings.PHONE_NUMBER
CHANNEL_USERNAME = settings.CHANNEL_USERNAME

# Validate environment variables
if not all([API_ID, API_HASH, PHONE_NUMBER, CHANNEL_USERNAME]):
    raise ValueError("Missing required environment variables")

# Configure output directory
OUTPUT_DIR = f"./{CHANNEL_USERNAME}_media/"


async def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    async with TelegramClient("session_name", int(API_ID), API_HASH) as client:
        await client.start(PHONE_NUMBER)

        if not await client.is_user_authorized():
            print("Authorization failed!")
            return

        channel = await client.get_entity(CHANNEL_USERNAME)
        print(f"Downloading media from: {channel.title}")

        total, skipped = 0, 0

        # Modified line: added limit=50 to iter_messages
        async for message in client.iter_messages(channel, limit=50):
            if not message.media:
                continue

            # Determine file extension
            if isinstance(message.media, MessageMediaPhoto):
                ext = ".jpg"
            elif isinstance(message.media, MessageMediaDocument):
                # Search for DocumentAttributeFilename in attributes
                filename_attr = next(
                    (
                        attr
                        for attr in message.media.document.attributes
                        if hasattr(attr, "file_name")
                    ),
                    None,
                )
                if filename_attr:
                    ext = f".{filename_attr.file_name.split('.')[-1]}"
                else:
                    # Fallback to mime type if available
                    mime_type = getattr(message.media.document, "mime_type", "")
                    if "image" in mime_type:
                        ext = ".jpg"
                    elif "audio" in mime_type:
                        ext = ".mp3"
                    elif "video" in mime_type:
                        ext = ".mp4"
                    else:
                        ext = ".unknown"
            else:
                continue

            filename = f"{message.id}{ext}"
            filepath = os.path.join(OUTPUT_DIR, filename)

            if os.path.exists(filepath):
                skipped += 1
                continue

            try:
                await client.download_media(message.media, file=filepath)
                print(f"Downloaded: {filename}")
                total += 1
            except Exception as e:
                print(f"Error downloading {filename}: {str(e)}")

        print(f"\nCompleted: {total} files downloaded")
        print(f"Skipped: {skipped} existing files")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
