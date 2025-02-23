from typing import Optional

from telethon import TelegramClient

from src.config import settings
from src.download_manager import DownloadManager
from src.progress import MultipleProgress


class TelegramDownloader:
    def __init__(self):
        self.api_id = settings.API_ID
        self.api_hash = settings.API_HASH
        self.phone_number = settings.PHONE_NUMBER
        self.channel_username = settings.CHANNEL_USERNAME
        self.client: Optional[TelegramClient] = None
        self.download_manager: Optional[DownloadManager] = None

    async def initialize(self):
        self.client = TelegramClient("session_name", self.api_id, self.api_hash)
        await self.client.start(self.phone_number)
        self.download_manager = DownloadManager(self.client)
        return self

    async def close(self):
        await self.client.disconnect()

    async def download_channel_media(self):
        if not await self.client.is_user_authorized():
            print("Authorization failed!")
            return

        channel = await self.client.get_entity(self.channel_username)
        print(f"Downloading media from: {channel.title}")
        if settings.DEBUG:
            print(
                f"Allowed formats: {'all' if settings.DOWNLOAD_ALL else ', '.join(settings.ALLOWED_FORMATS)}"
            )

        # Get total message count for progress bar
        total_messages = settings.HISTORY_LIMIT

        with MultipleProgress() as progress:
            self.download_manager.set_progress(progress)
            channel_task = progress.add_task(
                "[bold blue]Processing Messages",
                total=total_messages,
                progress_type="total",
            )

            async for message in self.client.iter_messages(
                channel, limit=settings.HISTORY_LIMIT, reverse=settings.REVERSE_ORDER
            ):
                success, result = await self.download_manager.download_file(message)
                progress.advance(channel_task)
                if success:
                    print(f"Downloaded: {result}")
                elif "not allowed" in result and settings.DEBUG:
                    print(result)
            progress.update(channel_task, description="[green]Download Complete 🎉")

    def print_statistics(self):
        statistics = self.download_manager.get_statistics()
        print(f"Completed: {statistics['total_downloads']} files downloaded")
        print(f"Skipped: {statistics['skipped_files']} existing files")
        print(f"Filtered: {statistics['filtered_files']} files (wrong format)")

    async def run(self):
        await self.initialize()
        await self.download_channel_media()
        self.print_statistics()
        await self.close()
