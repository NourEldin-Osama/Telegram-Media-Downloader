import asyncio

from telethon import TelegramClient

from config import settings
from download_manager import DownloadManager

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


async def main():
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

        download_manager = DownloadManager(client)

        async for message in client.iter_messages(
            channel, limit=settings.HISTORY_LIMIT, reverse=settings.REVERSE_ORDER
        ):
            success, result = await download_manager.download_file(message)
            if success:
                print(f"Downloaded: {result}")

        stats = download_manager.get_stats()
        print(f"\nCompleted: {stats['total_downloads']} files downloaded")
        print(f"Skipped: {stats['skipped_files']} existing files")
        print(f"Filtered: {stats['filtered_files']} files (wrong format)")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
