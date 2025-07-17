import asyncio
import os
import json
import time
from datetime import datetime
from telethon.sync import TelegramClient
from telethon.tl.functions.messages import ImportChatInviteRequest, ForwardMessagesRequest
from telethon.errors import FloodWaitError, MessageIdInvalidError, SessionPasswordNeededError
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from src.config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION_NAME, TELEGRAM_CACHE, PROGRESS_FILE, TELEGRAM_DIR
from src.utils import log

class TelegramManager:
    def __init__(self):
        self.client = None
        self.session_path = os.path.join(TELEGRAM_DIR, TELEGRAM_SESSION_NAME + '.session')
        
    async def initialize_client(self, api_id=None, api_hash=None):
        """Initialize Telegram client"""
        try:
            api_id = api_id or TELEGRAM_API_ID
            api_hash = api_hash or TELEGRAM_API_HASH
            
            self.client = TelegramClient(self.session_path, int(api_id), api_hash)
            await self.client.start()
            
            if not await self.client.is_user_authorized():
                log("❌ Telegram client not authorized. Please authorize first.")
                return False
            
            log("✅ Telegram client initialized successfully")
            return True
            
        except Exception as e:
            log(f"❌ Error initializing Telegram client: {str(e)}")
            return False
    
    async def get_channel_entity(self, channel_url):
        """Get channel entity from URL or username"""
        try:
            if not self.client:
                log("❌ Telegram client not initialized")
                return None
                
            # Handle different URL formats
            if channel_url.startswith('https://t.me/'):
                username = channel_url.replace('https://t.me/', '')
                if username.startswith('+'):
                    # Invite link
                    invite_hash = username[1:]
                    entity = await self.client(ImportChatInviteRequest(invite_hash))
                    return entity.chats[0]
                else:
                    # Regular username
                    entity = await self.client.get_entity(username)
                    return entity
            elif channel_url.startswith('@'):
                entity = await self.client.get_entity(channel_url)
                return entity
            else:
                # Assume it's a username without @
                entity = await self.client.get_entity('@' + channel_url)
                return entity
                
        except Exception as e:
            log(f"❌ Error getting channel entity: {str(e)}")
            return None
    
    async def get_channel_messages(self, channel_url, limit=100, message_filter='all', min_id=0):
        """Get messages from a Telegram channel with filtering"""
        try:
            if not self.client:
                await self.initialize_client()
                
            entity = await self.get_channel_entity(channel_url)
            if not entity:
                return []
            
            log(f"📥 Fetching messages from {entity.title or channel_url}")
            
            messages = []
            async for message in self.client.iter_messages(entity, limit=limit, min_id=min_id, reverse=True):
                if not message:
                    continue
                
                # Apply message filter
                if not self._message_matches_filter(message, message_filter):
                    continue
                
                message_data = {
                    'id': message.id,
                    'date': message.date.isoformat() if message.date else None,
                    'text': message.text or '',
                    'sender_id': message.sender_id,
                    'type': self._get_message_type(message),
                    'media_type': self._get_media_type(message),
                    'file_name': self._get_file_name(message),
                    'file_size': self._get_file_size(message),
                    'has_media': bool(message.media)
                }
                
                messages.append(message_data)
            
            # Save to cache
            with open(TELEGRAM_CACHE, 'w', encoding='utf-8') as f:
                json.dump(messages, f, ensure_ascii=False, indent=2)
            
            log(f"✅ Fetched {len(messages)} messages")
            return messages
            
        except Exception as e:
            log(f"❌ Error fetching messages: {str(e)}")
            return []
    
    def _message_matches_filter(self, message, message_filter):
        """Check if message matches the specified filter"""
        if message_filter == 'all':
            return True
        elif message_filter == 'text':
            return message.text and not message.media
        elif message_filter == 'photo':
            return isinstance(message.media, MessageMediaPhoto)
        elif message_filter == 'video':
            return isinstance(message.media, MessageMediaDocument) and message.media.document.mime_type.startswith('video/')
        elif message_filter == 'document':
            return isinstance(message.media, MessageMediaDocument) and not message.media.document.mime_type.startswith(('video/', 'audio/', 'image/'))
        elif message_filter == 'audio':
            return isinstance(message.media, MessageMediaDocument) and message.media.document.mime_type.startswith('audio/')
        return True
    
    def _get_message_type(self, message):
        """Get the type of message"""
        if message.text and not message.media:
            return 'text'
        elif message.media:
            return 'media'
        else:
            return 'other'
    
    def _get_media_type(self, message):
        """Get the media type of message"""
        if not message.media:
            return None
        
        if isinstance(message.media, MessageMediaPhoto):
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
    
    def _get_file_name(self, message):
        """Get the file name from message media"""
        if not message.media:
            return None
        
        if isinstance(message.media, MessageMediaDocument):
            for attr in message.media.document.attributes:
                if hasattr(attr, 'file_name') and attr.file_name:
                    return attr.file_name
        
        return None
    
    def _get_file_size(self, message):
        """Get the file size from message media"""
        if not message.media:
            return None
        
        if isinstance(message.media, MessageMediaDocument):
            return message.media.document.size
        
        return None
    
    async def forward_messages(self, source_channel, target_channel, message_ids):
        """Forward selected messages to target channel"""
        try:
            if not self.client:
                await self.initialize_client()
            
            source_entity = await self.get_channel_entity(source_channel)
            target_entity = await self.get_channel_entity(target_channel)
            
            if not source_entity or not target_entity:
                log("❌ Could not resolve source or target channel")
                return False
            
            log(f"📤 Starting to forward {len(message_ids)} messages")
            
            forwarded_count = 0
            for msg_id in message_ids:
                try:
                    await self.client(ForwardMessagesRequest(
                        from_peer=source_entity,
                        id=[int(msg_id)],
                        to_peer=target_entity
                    ))
                    
                    log(f"✅ Forwarded message {msg_id}")
                    forwarded_count += 1
                    self.save_last_id(msg_id)
                    
                    # Rate limiting
                    await asyncio.sleep(1.5)
                    
                except FloodWaitError as e:
                    log(f"⏳ Flood wait: {e.seconds} seconds. Waiting...")
                    await asyncio.sleep(e.seconds + 5)
                    continue
                    
                except MessageIdInvalidError:
                    log(f"⚠️ Skipped invalid message ID: {msg_id}")
                    continue
                    
                except Exception as e:
                    log(f"❌ Error forwarding message {msg_id}: {str(e)}")
                    continue
            
            log(f"🎉 Forwarding completed. {forwarded_count}/{len(message_ids)} messages forwarded.")
            return True
            
        except Exception as e:
            log(f"❌ Error in forward_messages: {str(e)}")
            return False
    
    async def download_media(self, channel_url, message_ids):
        """Download media from selected messages"""
        try:
            if not self.client:
                await self.initialize_client()
            
            entity = await self.get_channel_entity(channel_url)
            if not entity:
                return False
            
            log(f"💾 Starting to download media from {len(message_ids)} messages")
            
            downloaded_count = 0
            for msg_id in message_ids:
                try:
                    message = await self.client.get_messages(entity, ids=int(msg_id))
                    if not message or not message.media:
                        continue
                    
                    # Generate filename
                    file_name = self._get_file_name(message) or f"telegram_media_{msg_id}"
                    file_path = os.path.join(TELEGRAM_DIR, file_name)
                    
                    # Download the media
                    await self.client.download_media(message, file_path)
                    
                    log(f"✅ Downloaded: {file_name}")
                    downloaded_count += 1
                    
                except Exception as e:
                    log(f"❌ Error downloading media from message {msg_id}: {str(e)}")
                    continue
            
            log(f"🎉 Download completed. {downloaded_count}/{len(message_ids)} files downloaded.")
            return True
            
        except Exception as e:
            log(f"❌ Error in download_media: {str(e)}")
            return False
    
    def save_last_id(self, last_id):
        """Save the last processed message ID"""
        try:
            with open(PROGRESS_FILE, 'w') as f:
                f.write(str(last_id))
        except Exception as e:
            log(f"❌ Error saving last ID: {str(e)}")
    
    def load_last_id(self):
        """Load the last processed message ID"""
        try:
            if os.path.exists(PROGRESS_FILE):
                with open(PROGRESS_FILE, 'r') as f:
                    return int(f.read().strip())
        except Exception as e:
            log(f"❌ Error loading last ID: {str(e)}")
        return 0
    
    def get_cached_messages(self):
        """Get messages from cache"""
        try:
            if os.path.exists(TELEGRAM_CACHE):
                with open(TELEGRAM_CACHE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            log(f"❌ Error loading cached messages: {str(e)}")
        return []
    
    async def close(self):
        """Close the Telegram client"""
        if self.client:
            await self.client.disconnect()

# Global instance
telegram_manager = TelegramManager()

def run_async_function(func, *args, **kwargs):
    """Helper function to run async functions in sync context"""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # If loop is already running, create a new thread
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, func(*args, **kwargs))
                return future.result()
        else:
            return loop.run_until_complete(func(*args, **kwargs))
    except RuntimeError:
        # No event loop, create a new one
        return asyncio.run(func(*args, **kwargs))

