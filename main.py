import asyncio

from src.telegram_downloader import TelegramDownloader

if __name__ == "__main__":
    app = TelegramDownloader()
    try:
        asyncio.run(app.run())
    except KeyboardInterrupt:
        print("\nOperation cancelled by user")
