"""
Bot Manager Backend - Flask Application
Handles bot management, chat functionality, and GitHub integration
"""

import os
import json
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CHATS_DIR = DATA_DIR / "chats"
BOTS_FILE = DATA_DIR / "bots.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CHATS_DIR.mkdir(exist_ok=True)

# Initialize bots.json if it doesn't exist
if not BOTS_FILE.exists():
    with open(BOTS_FILE, 'w') as f:
        json.dump([], f)

# DeepSeek API configuration
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_MODEL = "deepseek-chat"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

# GitHub API configuration
GITHUB_API_URL = "https://api.github.com"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


class BotManager:
    """Manages bot operations and data persistence"""
    
    @staticmethod
    def load_bots() -> List[Dict]:
        """Load all bots from JSON file"""
        try:
            with open(BOTS_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []
    
    @staticmethod
    def save_bots(bots: List[Dict]) -> None:
        """Save bots to JSON file"""
        with open(BOTS_FILE, 'w') as f:
            json.dump(bots, f, indent=2)
    
    @staticmethod
    def get_bot(bot_id: str) -> Optional[Dict]:
        """Get a specific bot by ID"""
        bots = BotManager.load_bots()
        for bot in bots:
            if bot.get('id') == bot_id:
                return bot
        return None
    
    @staticmethod
    def create_bot(bot_data: Dict) -> Dict:
        """Create a new bot"""
        bots = BotManager.load_bots()
        
        bot_id = str(uuid.uuid4())
        new_bot = {
            'id': bot_id,
            'name': bot_data.get('name', 'Unnamed Bot'),
            'system_prompt': bot_data.get('system_prompt', 'You are a helpful assistant.'),
            'temperature': float(bot_data.get('temperature', 0.7)),
            'max_tokens': int(bot_data.get('max_tokens', 2048)),
            'model': DEEPSEEK_MODEL,
            'provider': 'DeepSeek',
            'is_active': True,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'message_count': 0,
            'token_count': 0
        }
        
        bots.append(new_bot)
        BotManager.save_bots(bots)
        
        # Create chat directory for this bot
        bot_chat_dir = CHATS_DIR / bot_id
        bot_chat_dir.mkdir(exist_ok=True)
        
        return new_bot
    
    @staticmethod
    def update_bot(bot_id: str, update_data: Dict) -> Optional[Dict]:
        """Update an existing bot"""
        bots = BotManager.load_bots()
        
        for i, bot in enumerate(bots):
            if bot.get('id') == bot_id:
                # Update allowed fields
                allowed_fields = ['name', 'system_prompt', 'temperature', 
                                 'max_tokens', 'is_active']
                for field in allowed_fields:
                    if field in update_data:
                        bots[i][field] = update_data[field]
                
                bots[i]['updated_at'] = datetime.now().isoformat()
                BotManager.save_bots(bots)
                return bots[i]
        
        return None
    
    @staticmethod
    def delete_bot(bot_id: str) -> bool:
        """Delete a bot and its chat history"""
        bots = BotManager.load_bots()
        
        # Remove bot from list
        new_bots = [bot for bot in bots if bot.get('id') != bot_id]
        
        if len(new_bots) != len(bots):
            BotManager.save_bots(new_bots)
            
            # Delete chat directory
            bot_chat_dir = CHATS_DIR / bot_id
            if bot_chat_dir.exists():
                import shutil
                shutil.rmtree(bot_chat_dir)
            
            return True
        
        return False
    
    @staticmethod
    def increment_message_count(bot_id: str, tokens_used: int) -> None:
        """Increment message and token count for a bot"""
        bots = BotManager.load_bots()
        
        for i, bot in enumerate(bots):
            if bot.get('id') == bot_id:
                bots[i]['message_count'] = bots[i].get('message_count', 0) + 1
                bots[i]['token_count'] = bots[i].get('token_count', 0) + tokens_used
                bots[i]['updated_at'] = datetime.now().isoformat()
                BotManager.save_bots(bots)
                break


class ChatManager:
    """Manages chat conversations and history"""
    
    @staticmethod
    def get_chat_history(bot_id: str, limit: int = 50) -> List[Dict]:
        """Get chat history for a specific bot"""
        bot_chat_dir = CHATS_DIR / bot_id
        
        if not bot_chat_dir.exists():
            return []
        
        # Get all chat files, sorted by modification time (newest first)
        chat_files = sorted(bot_chat_dir.glob('*.json'), 
                          key=lambda x: x.stat().st_mtime, 
                          reverse=True)
        
        all_messages = []
        for chat_file in chat_files[:limit]:
            try:
                with open(chat_file, 'r') as f:
                    chat_data = json.load(f)
                    all_messages.extend(chat_data.get('messages', []))
            except (json.JSONDecodeError, FileNotFoundError):
                continue
        
        return all_messages
    
    @staticmethod
    def save_message(bot_id: str, message: Dict, response: Dict) -> str:
        """Save a message and response to chat history"""
        bot_chat_dir = CHATS_DIR / bot_id
        bot_chat_dir.mkdir(exist_ok=True)
        
        # Create filename based on date
        date_str = datetime.now().strftime('%Y-%m-%d')
        chat_file = bot_chat_dir / f"{date_str}.json"
        
        # Load existing chat or create new
        if chat_file.exists():
            try:
                with open(chat_file, 'r') as f:
                    chat_data = json.load(f)
            except json.JSONDecodeError:
                chat_data = {'messages': []}
        else:
            chat_data = {'messages': []}
        
        # Add new message and response
        timestamp = datetime.now().isoformat()
        
        chat_data['messages'].append({
            'role': 'user',
            'content': message.get('content', ''),
            'timestamp': timestamp,
            'tokens': message.get('tokens', 0)
        })
        
        chat_data['messages'].append({
            'role': 'assistant',
            'content': response.get('content', ''),
            'timestamp': timestamp,
            'tokens': response.get('tokens', 0),
            'response_time': response.get('response_time', 0)
        })
        
        # Save to file
        with open(chat_file, 'w') as f:
            json.dump(chat_data, f, indent=2)
        
        return timestamp
    
    @staticmethod
    def clear_chat_history(bot_id: str) -> bool:
        """Clear all chat history for a bot"""
        bot_chat_dir = CHATS_DIR / bot_id
        
        if bot_chat_dir.exists():
            import shutil
            shutil.rmtree(bot_chat_dir)
            bot_chat_dir.mkdir(exist_ok=True)
            return True
        
        return False
    
    @staticmethod
    def export_chat_history(bot_id: str) -> Optional[str]:
        """Export chat history as text"""
        messages = ChatManager.get_chat_history(bot_id, limit=1000)
        
        if not messages:
            return None
        
        export_text = f"Chat History for Bot: {bot_id}\n"
        export_text += f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        export_text += "=" * 50 + "\n\n"
        
        for msg in messages:
            role = "User" if msg.get('role') == 'user' else "Assistant"
            timestamp = msg.get('timestamp', '')
            content = msg.get('content', '')
            
            export_text += f"[{timestamp}] {role}:\n"
            export_text += f"{content}\n"
            export_text += "-" * 30 + "\n"
        
        return export_text


class DeepSeekAPI:
    """Handles communication with DeepSeek API"""
    
    @staticmethod
    def send_message(bot: Dict, messages: List[Dict]) -> Dict:
        """Send message to DeepSeek API and get response"""
        if not DEEPSEEK_API_KEY:
            raise ValueError("DeepSeek API key not configured")
        
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Prepare conversation with system prompt
        conversation = [{'role': 'system', 'content': bot.get('system_prompt', '')}]
        conversation.extend(messages)
        
        payload = {
            'model': DEEPSEEK_MODEL,
            'messages': conversation,
            'temperature': bot.get('temperature', 0.7),
            'max_tokens': bot.get('max_tokens', 2048),
            'stream': False
        }
        
        start_time = time.time()
        
        try:
            response = requests.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            
            response_data = response.json()
            response_time = time.time() - start_time
            
            # Extract response content
            if 'choices' in response_data and len(response_data['choices']) > 0:
                content = response_data['choices'][0]['message']['content']
                tokens_used = response_data.get('usage', {}).get('total_tokens', 0)
                
                return {
                    'success': True,
                    'content': content,
                    'tokens': tokens_used,
                    'response_time': round(response_time, 2)
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from API'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'API request failed: {str(e)}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Unexpected error: {str(e)}'
            }


class GitHubManager:
    """Handles GitHub integration for pushing bot data"""
    
    @staticmethod
    def create_repo(token: str, repo_name: str, description: str = "") -> Dict:
        """Create a new GitHub repository"""
        headers = {
            'Authorization': f'token {token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        payload = {
            'name': repo_name,
            'description': description,
            'private': False,
            'auto_init': False
        }
        
        try:
            response = requests.post(
                f'{GITHUB_API_URL}/user/repos',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 201:
                return {
                    'success': True,
                    'repo_url': response.json().get('html_url'),
                    'clone_url': response.json().get('clone_url')
                }
            else:
                return {
                    'success': False,
                    'error': f'Failed to create repo: {response.text}'
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f'GitHub API request failed: {str(e)}'
            }
    
    @staticmethod
    def push_to_github(token: str, repo_name: str, username: str) -> Dict:
        """Push bot data to GitHub repository"""
        # This is a simplified version - in production, you'd use git commands
        # or the GitHub API to create files
        
        # For now, we'll just create the repo and return success
        # In a real implementation, you would:
        # 1. Initialize a git repository
        # 2. Add all bot files
        # 3. Commit and push
        
        result = GitHubManager.create_repo(token, repo_name, "Bot Manager Export")
        
        if result['success']:
            return {
                'success': True,
                'message': f'Repository created: {result["repo_url"]}',
                'url': result['repo_url']
            }
        else:
            return result


class Analytics:
    """Handles analytics and