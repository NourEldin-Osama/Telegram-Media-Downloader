import asyncio

from telethon import TelegramClient, errors

from config import settings


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
