import asyncio

from telegram_downloader import get_file_extension, should_download_file
from telethon import TelegramClient, errors
from telethon.tl.types import DocumentAttributeFilename, MessageMediaDocument

from config import settings


def get_file_name(message) -> str:
    """Get the original filename from a message"""
    if isinstance(message.media, MessageMediaDocument):
        for attr in message.media.document.attributes:
            if isinstance(attr, DocumentAttributeFilename):
                return attr.file_name
    # Fallback to message ID with extension
    return f"{message.id}{get_file_extension(message)}"


async def test_connection():
    """Test Telegram connection and channel access"""
    try:
        # Initialize client
        client = TelegramClient(
            session="session_name",
            api_id=settings.API_ID,
            api_hash=settings.API_HASH,
        )

        # Test connection
        print("⌛ Connecting to Telegram...")
        await client.connect()

        # Test authentication
        if not await client.is_user_authorized():
            print("⌛ Sending login code...")
            await client.send_code_request(settings.PHONE_NUMBER)
            await client.sign_in(
                phone=settings.PHONE_NUMBER,
                code=input("✉️ Enter verification code: "),
            )

        # Test channel access
        print("⌛ Checking channel access...")
        channel = await client.get_entity(settings.CHANNEL_USERNAME)
        print(f"\n✅ Successfully accessed channel: {channel.title} (ID: {channel.id})")

        # Get some basic info
        async for message in client.iter_messages(channel, limit=1):
            if message:
                print(f"📅 Last message date: {message.date}")

        # Test finding latest audio file
        print("\n⌛ Checking for latest audio file...")
        latest_audio = None
        async for message in client.iter_messages(channel, limit=50):
            if message.media:
                ext = get_file_extension(message)
                if ext and should_download_file(ext):
                    latest_audio = message
                    break

        if latest_audio:
            filename = get_file_name(latest_audio)
            print(f"🎵 Latest audio file found: {filename}")
        else:
            print("ℹ️ No audio files found in the last 50 messages")

        return True

    except errors.ApiIdInvalidError:
        print("❌ Invalid API ID/HASH combination")
    except errors.PhoneNumberInvalidError:
        print("❌ Invalid phone number format")
    except errors.PhoneCodeInvalidError:
        print("❌ Invalid verification code")
    except errors.ChannelPrivateError:
        print("❌ You don't have access to this private channel")
    except errors.ChannelInvalidError:
        print("❌ Channel username is invalid or inaccessible")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

    return False


if __name__ == "__main__":
    print("🚀 Starting connection test...\n")
    result = asyncio.run(test_connection())

    if result:
        print("\n✨ All checks passed! You can proceed with downloading media.")
    else:
        print("\n🔴 Connection test failed. Check your credentials and channel access.")
