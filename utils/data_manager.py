"""
utils/data_manager.py
Data management utilities for Bot Manager application
"""

import os
import json
import shutil
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Union
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataManager:
    """Manages data storage and retrieval for bots and chats"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Initialize DataManager with data directory
        
        Args:
            data_dir: Root directory for data storage
        """
        self.data_dir = data_dir
        self.bots_file = os.path.join(data_dir, "bots.json")
        self.chats_dir = os.path.join(data_dir, "chats")
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """Create necessary directories if they don't exist"""
        try:
            os.makedirs(self.data_dir, exist_ok=True)
            os.makedirs(self.chats_dir, exist_ok=True)
            
            # Initialize bots.json if it doesn't exist
            if not os.path.exists(self.bots_file):
                with open(self.bots_file, 'w') as f:
                    json.dump([], f)
        except Exception as e:
            logger.error(f"Error creating directories: {e}")
            raise
    
    def load_bots(self) -> List[Dict[str, Any]]:
        """
        Load all bots from bots.json
        
        Returns:
            List of bot dictionaries
        """
        try:
            if not os.path.exists(self.bots_file):
                return []
            
            with open(self.bots_file, 'r') as f:
                bots = json.load(f)
            
            # Ensure each bot has required fields
            for bot in bots:
                bot.setdefault('id', '')
                bot.setdefault('name', '')
                bot.setdefault('system_prompt', '')
                bot.setdefault('temperature', 0.7)
                bot.setdefault('max_tokens', 2048)
                bot.setdefault('model', 'deepseek-chat')
                bot.setdefault('created_at', datetime.now().isoformat())
                bot.setdefault('updated_at', datetime.now().isoformat())
                bot.setdefault('is_active', True)
                bot.setdefault('message_count', 0)
                bot.setdefault('token_count', 0)
            
            return bots
        except json.JSONDecodeError:
            logger.error("bots.json contains invalid JSON")
            return []
        except Exception as e:
            logger.error(f"Error loading bots: {e}")
            return []
    
    def save_bots(self, bots: List[Dict[str, Any]]) -> bool:
        """
        Save bots to bots.json
        
        Args:
            bots: List of bot dictionaries
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Sort bots by creation date (newest first)
            bots.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            with open(self.bots_file, 'w') as f:
                json.dump(bots, f, indent=2)
            
            logger.info(f"Saved {len(bots)} bots to {self.bots_file}")
            return True
        except Exception as e:
            logger.error(f"Error saving bots: {e}")
            return False
    
    def get_bot(self, bot_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific bot by ID
        
        Args:
            bot_id: Bot ID to retrieve
            
        Returns:
            Bot dictionary or None if not found
        """
        bots = self.load_bots()
        for bot in bots:
            if bot.get('id') == bot_id:
                return bot
        return None
    
    def create_bot(self, bot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new bot
        
        Args:
            bot_data: Bot data dictionary
            
        Returns:
            Created bot dictionary or None if failed
        """
        try:
            bots = self.load_bots()
            
            # Generate unique ID
            import uuid
            bot_id = str(uuid.uuid4())
            
            # Create bot object with defaults
            bot = {
                'id': bot_id,
                'name': bot_data.get('name', 'Unnamed Bot'),
                'system_prompt': bot_data.get('system_prompt', 'You are a helpful AI assistant.'),
                'temperature': float(bot_data.get('temperature', 0.7)),
                'max_tokens': int(bot_data.get('max_tokens', 2048)),
                'model': 'deepseek-chat',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'is_active': True,
                'message_count': 0,
                'token_count': 0,
                'provider': 'DeepSeek'
            }
            
            bots.append(bot)
            
            if self.save_bots(bots):
                # Create chat directory for this bot
                bot_chat_dir = os.path.join(self.chats_dir, bot_id)
                os.makedirs(bot_chat_dir, exist_ok=True)
                
                logger.info(f"Created bot: {bot['name']} (ID: {bot_id})")
                return bot
            
            return None
        except Exception as e:
            logger.error(f"Error creating bot: {e}")
            return None
    
    def update_bot(self, bot_id: str, bot_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Update an existing bot
        
        Args:
            bot_id: Bot ID to update
            bot_data: Updated bot data
            
        Returns:
            Updated bot dictionary or None if not found/failed
        """
        try:
            bots = self.load_bots()
            updated = False
            
            for i, bot in enumerate(bots):
                if bot.get('id') == bot_id:
                    # Update allowed fields
                    if 'name' in bot_data:
                        bots[i]['name'] = bot_data['name']
                    if 'system_prompt' in bot_data:
                        bots[i]['system_prompt'] = bot_data['system_prompt']
                    if 'temperature' in bot_data:
                        bots[i]['temperature'] = float(bot_data['temperature'])
                    if 'max_tokens' in bot_data:
                        bots[i]['max_tokens'] = int(bot_data['max_tokens'])
                    if 'is_active' in bot_data:
                        bots[i]['is_active'] = bool(bot_data['is_active'])
                    
                    bots[i]['updated_at'] = datetime.now().isoformat()
                    updated = True
                    break
            
            if updated and self.save_bots(bots):
                logger.info(f"Updated bot: {bot_id}")
                return self.get_bot(bot_id)
            
            return None
        except Exception as e:
            logger.error(f"Error updating bot: {e}")
            return None
    
    def delete_bot(self, bot_id: str) -> bool:
        """
        Delete a bot and its chat history
        
        Args:
            bot_id: Bot ID to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bots = self.load_bots()
            original_count = len(bots)
            
            # Filter out the bot to delete
            bots = [bot for bot in bots if bot.get('id') != bot_id]
            
            if len(bots) < original_count:
                # Delete chat directory for this bot
                bot_chat_dir = os.path.join(self.chats_dir, bot_id)
                if os.path.exists(bot_chat_dir):
                    shutil.rmtree(bot_chat_dir)
                
                if self.save_bots(bots):
                    logger.info(f"Deleted bot: {bot_id}")
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error deleting bot: {e}")
            return False
    
    def increment_bot_stats(self, bot_id: str, messages: int = 1, tokens: int = 0) -> bool:
        """
        Increment bot message and token counts
        
        Args:
            bot_id: Bot ID
            messages: Number of messages to add
            tokens: Number of tokens to add
            
        Returns:
            True if successful, False otherwise
        """
        try:
            bots = self.load_bots()
            
            for i, bot in enumerate(bots):
                if bot.get('id') == bot_id:
                    bots[i]['message_count'] = bots[i].get('message_count', 0) + messages
                    bots[i]['token_count'] = bots[i].get('token_count', 0) + tokens
                    bots[i]['updated_at'] = datetime.now().isoformat()
                    break
            
            return self.save_bots(bots)
        except Exception as e:
            logger.error(f"Error incrementing bot stats: {e}")
            return False
    
    def save_chat(self, bot_id: str, messages: List[Dict[str, Any]], 
                  metadata: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Save chat messages to file
        
        Args:
            bot_id: Bot ID
            messages: List of message dictionaries
            metadata: Additional metadata to save
            
        Returns:
            File path if successful, None otherwise
        """
        try:
            bot_chat_dir = os.path.join(self.chats_dir, bot_id)
            os.makedirs(bot_chat_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"chat_{timestamp}.json"
            filepath = os.path.join(bot_chat_dir, filename)
            
            chat_data = {
                'bot_id': bot_id,
                'timestamp': datetime.now().isoformat(),
                'messages': messages,
                'metadata': metadata or {}
            }
            
            with open(filepath, 'w') as f:
                json.dump(chat_data, f, indent=2)
            
            logger.info(f"Saved chat to: {filepath}")
            return filepath
        except Exception as e:
            logger.error(f"Error saving chat: {e}")
            return None
    
    def load_chat_history(self, bot_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Load chat history for a bot
        
        Args:
            bot_id: Bot ID
            limit: Maximum number of chat files to load
            
        Returns:
            List of chat dictionaries
        """
        try:
            bot_chat_dir = os.path.join(self.chats_dir, bot_id)
            
            if not os.path.exists(bot_chat_dir):
                return []
            
            # Get all chat files, sorted by modification time (newest first)
            chat_files = []
            for filename in os.listdir(bot_chat_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(bot_chat_dir, filename)
                    mtime = os.path.getmtime(filepath)
                    chat_files.append((mtime, filepath))
            
            chat_files.sort(reverse=True)  # Newest first
            chat_files = chat_files[:limit]  # Apply limit
            
            chats = []
            for _, filepath in chat_files:
                try:
                    with open(filepath, 'r') as f:
                        chat_data = json.load(f)
                    chats.append(chat_data)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in chat file: {