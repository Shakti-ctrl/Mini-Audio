#!/usr/bin/env python3
"""
Standalone Telegram Bot for Channel Message Extraction and Forwarding
This script demonstrates the real functionality using the provided credentials.
"""

import asyncio
import os
import json
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest, ForwardMessagesRequest
from telethon.errors import FloodWaitError, MessageIdInvalidError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument

# ================= CONFIG =================
api_id = 28403662
api_hash = '079509d4ac7f209a1a58facd00d6ff5a'
bot_token = '8154976061:AAH_91bkAMJ7AJi-TEfZLx3KztFLJs6nM4g'
phone_number = '+917352013479'

# Default channels for testing
default_source_channel = 'https://t.me/arjunaa_neet_25'
test_channels = [
    '@telegram',
    '@durov',
    'https://t.me/telegram',
    'https://t.me/arjunaa_neet_25'
]

session_name = 'telegram_bot_session'
output_dir = 'telegram_downloads'

# ============== Helper Functions ==============

def ensure_directory(path):
    """Ensure directory exists"""
    if not os.path.exists(path):
        os.makedirs(path)

def get_media_type(message):
    """Get media type from message"""
    if not message.media:
        return 'text'
    elif isinstance(message.media, MessageMediaPhoto):
        return 'photo'
    elif isinstance(message.media, MessageMediaDocument):
        mime_type = message.media.document.mime_type
        if mime_type.startswith('video/'):
            return 'video'
        elif mime_type.startswith('audio/'):
            return 'audio'
        elif mime_type.startswith('image/'):
            return 'image'
        else:
            return 'document'
    else:
        return 'other'

def get_file_name(message):
    """Get file name from message media"""
    if not message.media:
        return None
    
    if isinstance(message.media, MessageMediaDocument):
        for attr in message.media.document.attributes:
            if hasattr(attr, 'file_name') and attr.file_name:
                return attr.file_name
    
    return f"telegram_file_{message.id}"

def filter_message(message, message_filter):
    """Filter messages based on type"""
    if not message:
        return False
        
    if message_filter == 'all':
        return True
    elif message_filter == 'text':
        return message.text and not message.media
    elif message_filter == 'photos':
        return isinstance(message.media, MessageMediaPhoto)
    elif message_filter == 'videos':
        return isinstance(message.media, MessageMediaDocument) and message.media.document.mime_type.startswith('video/')
    elif message_filter == 'documents':
        return isinstance(message.media, MessageMediaDocument) and not message.media.document.mime_type.startswith(('video/', 'audio/', 'image/'))
    elif message_filter == 'audio':
        return isinstance(message.media, MessageMediaDocument) and message.media.document.mime_type.startswith('audio/')
    
    return False

# ============== Main Functions ==============

async def search_channel_messages(client, channel_url, limit=50, message_filter='all'):
    """Search and display messages from a Telegram channel"""
    try:
        print(f"🔍 Searching channel: {channel_url}")
        
        # Get channel entity
        try:
            entity = await client.get_entity(channel_url)
            print(f"✅ Found channel: {entity.title if hasattr(entity, 'title') else channel_url}")
        except Exception as e:
            print(f"❌ Error getting channel entity: {e}")
            return []
        
        # Fetch messages
        messages = []
        print(f"📥 Fetching messages (limit: {limit}, filter: {message_filter})...")
        
        async for message in client.iter_messages(entity, limit=limit):
            if not message:
                continue
            
            # Apply filter
            if not filter_message(message, message_filter):
                continue
            
            message_data = {
                'id': message.id,
                'date': message.date.strftime('%Y-%m-%d %H:%M:%S') if message.date else '',
                'text': (message.text or '')[:100] + ('...' if len(message.text or '') > 100 else ''),
                'media_type': get_media_type(message),
                'file_name': get_file_name(message),
                'has_media': bool(message.media),
                'sender_id': message.sender_id,
                'views': getattr(message, 'views', 0) or 0
            }
            
            messages.append(message_data)
        
        print(f"✅ Found {len(messages)} messages matching filter '{message_filter}'")
        
        # Display results
        if messages:
            print("\\n📋 MESSAGE RESULTS:")
            print("-" * 80)
            for i, msg in enumerate(messages[:10], 1):  # Show first 10
                print(f"{i:2d}. ID: {msg['id']} | Date: {msg['date']} | Type: {msg['media_type']}")
                if msg['text']:
                    print(f"    Text: {msg['text']}")
                if msg['file_name']:
                    print(f"    File: {msg['file_name']}")
                if msg['views']:
                    print(f"    Views: {msg['views']}")
                print()
            
            if len(messages) > 10:
                print(f"... and {len(messages) - 10} more messages")
        
        # Save to JSON file
        output_file = f"messages_{channel_url.replace('/', '_').replace('@', '').replace(':', '')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Results saved to: {output_file}")
        return messages
        
    except Exception as e:
        print(f"❌ Error searching messages: {e}")
        return []

async def download_media_from_messages(client, channel_url, message_ids, download_dir):
    """Download media files from selected messages"""
    try:
        ensure_directory(download_dir)
        
        entity = await client.get_entity(channel_url)
        print(f"💾 Downloading media from {len(message_ids)} messages...")
        
        downloaded_count = 0
        for msg_id in message_ids:
            try:
                message = await client.get_messages(entity, ids=int(msg_id))
                if not message or not message.media:
                    continue
                
                # Generate filename
                file_name = get_file_name(message)
                if not file_name:
                    media_type = get_media_type(message)
                    file_name = f"{media_type}_{msg_id}"
                
                file_path = os.path.join(download_dir, file_name)
                
                # Download the media
                await client.download_media(message, file_path)
                
                print(f"✅ Downloaded: {file_name}")
                downloaded_count += 1
                
            except Exception as e:
                print(f"❌ Error downloading media from message {msg_id}: {e}")
                continue
        
        print(f"🎉 Download completed. {downloaded_count}/{len(message_ids)} files downloaded.")
        return downloaded_count > 0
        
    except Exception as e:
        print(f"❌ Error in download_media: {e}")
        return False

async def forward_messages_to_channel(client, source_channel, target_channel, message_ids):
    """Forward selected messages to target channel"""
    try:
        source_entity = await client.get_entity(source_channel)
        target_entity = await client.get_entity(target_channel)
        
        print(f"📤 Forwarding {len(message_ids)} messages from {source_channel} to {target_channel}")
        
        forwarded_count = 0
        for msg_id in message_ids:
            try:
                await client(ForwardMessagesRequest(
                    from_peer=source_entity,
                    id=[int(msg_id)],
                    to_peer=target_entity
                ))
                
                print(f"✅ Forwarded message {msg_id}")
                forwarded_count += 1
                
                # Rate limiting
                await asyncio.sleep(1.5)
                
            except FloodWaitError as e:
                print(f"⏳ Flood wait: {e.seconds} seconds. Waiting...")
                await asyncio.sleep(e.seconds + 5)
                continue
                
            except MessageIdInvalidError:
                print(f"⚠️ Skipped invalid message ID: {msg_id}")
                continue
                
            except Exception as e:
                print(f"❌ Error forwarding message {msg_id}: {e}")
                continue
        
        print(f"🎉 Forwarding completed. {forwarded_count}/{len(message_ids)} messages forwarded.")
        return forwarded_count > 0
        
    except Exception as e:
        print(f"❌ Error in forward_messages: {e}")
        return False

# ============== Interactive Menu ==============

def show_menu():
    """Display the main menu"""
    print("\\n" + "="*60)
    print("🤖 TELEGRAM CHANNEL EXTRACTOR & FORWARDER")
    print("="*60)
    print("1. 🔍 Search Channel Messages")
    print("2. 💾 Download Media from Messages")
    print("3. 📤 Forward Messages to Channel")
    print("4. 📋 Test Multiple Channels")
    print("5. ⚙️  Show Configuration")
    print("0. 🚪 Exit")
    print("="*60)

async def interactive_menu(client):
    """Interactive menu for testing functionality"""
    while True:
        show_menu()
        choice = input("\\nEnter your choice (0-5): ").strip()
        
        if choice == '0':
            print("👋 Goodbye!")
            break
        
        elif choice == '1':
            # Search channel messages
            channel = input(f"Enter channel URL (default: {default_source_channel}): ").strip()
            if not channel:
                channel = default_source_channel
            
            limit = input("Enter message limit (default: 20): ").strip()
            limit = int(limit) if limit.isdigit() else 20
            
            print("\\nMessage filters:")
            print("1. all  2. text  3. photos  4. videos  5. documents  6. audio")
            filter_choice = input("Choose filter (default: all): ").strip()
            
            filters = {'1': 'all', '2': 'text', '3': 'photos', '4': 'videos', '5': 'documents', '6': 'audio'}
            message_filter = filters.get(filter_choice, 'all')
            
            await search_channel_messages(client, channel, limit, message_filter)
        
        elif choice == '2':
            # Download media
            channel = input(f"Enter channel URL (default: {default_source_channel}): ").strip()
            if not channel:
                channel = default_source_channel
            
            message_ids = input("Enter message IDs (comma-separated): ").strip().split(',')
            message_ids = [mid.strip() for mid in message_ids if mid.strip().isdigit()]
            
            if not message_ids:
                print("❌ No valid message IDs provided")
                continue
            
            download_dir = input(f"Download directory (default: {output_dir}): ").strip()
            if not download_dir:
                download_dir = output_dir
            
            await download_media_from_messages(client, channel, message_ids, download_dir)
        
        elif choice == '3':
            # Forward messages
            source = input(f"Source channel (default: {default_source_channel}): ").strip()
            if not source:
                source = default_source_channel
            
            target = input("Target channel URL: ").strip()
            if not target:
                print("❌ Target channel is required")
                continue
            
            message_ids = input("Enter message IDs to forward (comma-separated): ").strip().split(',')
            message_ids = [mid.strip() for mid in message_ids if mid.strip().isdigit()]
            
            if not message_ids:
                print("❌ No valid message IDs provided")
                continue
            
            await forward_messages_to_channel(client, source, target, message_ids)
        
        elif choice == '4':
            # Test multiple channels
            print("\\n🧪 Testing multiple channels...")
            for channel in test_channels:
                print(f"\\n--- Testing: {channel} ---")
                messages = await search_channel_messages(client, channel, 5, 'all')
                if messages:
                    print(f"✅ {channel}: Found {len(messages)} messages")
                else:
                    print(f"❌ {channel}: No messages found or error occurred")
                await asyncio.sleep(2)  # Rate limiting
        
        elif choice == '5':
            # Show configuration
            print("\\n⚙️  CURRENT CONFIGURATION:")
            print(f"API ID: {api_id}")
            print(f"API Hash: {api_hash[:10]}...")
            print(f"Bot Token: {bot_token[:20]}...")
            print(f"Phone: {phone_number}")
            print(f"Session: {session_name}")
            print(f"Output Dir: {output_dir}")
            print(f"Default Channel: {default_source_channel}")
        
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\\nPress Enter to continue...")

# ============== Main Function ==============

async def main():
    """Main function"""
    print("🚀 Starting Telegram Channel Extractor & Forwarder...")
    print(f"📱 Using API ID: {api_id}")
    print(f"🔑 Using Bot Token: {bot_token[:20]}...")
    
    # Initialize client
    client = TelegramClient(session_name, api_id, api_hash)
    
    try:
        # Start client with bot token
        await client.start(bot_token=bot_token)
        print("✅ Connected to Telegram successfully!")
        
        # Test connection
        me = await client.get_me()
        print(f"🤖 Bot info: {me.first_name} (@{me.username})")
        
        # Run interactive menu
        await interactive_menu(client)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\\n💡 Trying with phone number authentication...")
        
        try:
            await client.start(phone=phone_number)
            print("✅ Connected with phone number!")
            
            # Run interactive menu
            await interactive_menu(client)
            
        except Exception as e2:
            print(f"❌ Phone authentication also failed: {e2}")
            print("\\n🔧 Please check your credentials and try again.")
    
    finally:
        await client.disconnect()
        print("\\n👋 Disconnected from Telegram.")

# ============== Entry Point ==============

if __name__ == "__main__":
    print("="*60)
    print("🤖 TELEGRAM CHANNEL EXTRACTOR & FORWARDER")
    print("   Standalone Bot with Real Data Integration")
    print("="*60)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\\n\\n⚠️  Interrupted by user. Goodbye!")
    except Exception as e:
        print(f"\\n❌ Fatal error: {e}")

