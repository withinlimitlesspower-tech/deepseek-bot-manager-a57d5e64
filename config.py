"""
config.py - Configuration settings for Bot Manager application
"""

import os
from pathlib import Path
from typing import Dict, Any

# Base directory
BASE_DIR = Path(__file__).parent

# Data directories
DATA_DIR = BASE_DIR / "data"
CHATS_DIR = DATA_DIR / "chats"
BOTS_FILE = DATA_DIR / "bots.json"

# Ensure directories exist
DATA_DIR.mkdir(exist_ok=True)
CHATS_DIR.mkdir(exist_ok=True)

# Flask configuration
class Config:
    """Flask application configuration"""
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    
    # File upload settings
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # Session settings
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = 3600  # 1 hour
    
    # CORS settings (if needed for future extensions)
    CORS_HEADERS = 'Content-Type'

# DeepSeek API configuration
class DeepSeekConfig:
    """DeepSeek API configuration"""
    
    # API endpoints
    BASE_URL = "https://api.deepseek.com"
    CHAT_COMPLETION_URL = f"{BASE_URL}/v1/chat/completions"
    
    # Default model
    DEFAULT_MODEL = "deepseek-chat"
    
    # Default parameters
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048
    DEFAULT_TOP_P = 1.0
    
    # Rate limiting
    MAX_RETRIES = 3
    RETRY_DELAY = 1  # seconds
    
    # Timeout settings
    REQUEST_TIMEOUT = 30  # seconds

# GitHub API configuration
class GitHubConfig:
    """GitHub API configuration"""
    
    # API endpoints
    BASE_URL = "https://api.github.com"
    USER_REPOS_URL = f"{BASE_URL}/user/repos"
    CREATE_REPO_URL = f"{BASE_URL}/user/repos"
    
    # Repository settings
    DEFAULT_DESCRIPTION = "Bot Manager Application - Managed by Bot Manager"
    DEFAULT_LICENSE = "mit"
    DEFAULT_VISIBILITY = "public"
    
    # File settings
    COMMIT_MESSAGE = "Initial commit from Bot Manager"
    BRANCH_NAME = "main"

# Application constants
class AppConstants:
    """Application-wide constants"""
    
    # Bot settings
    BOT_NAME_MIN_LENGTH = 1
    BOT_NAME_MAX_LENGTH = 50
    SYSTEM_PROMPT_MIN_LENGTH = 1
    SYSTEM_PROMPT_MAX_LENGTH = 2000
    
    # Chat settings
    MESSAGE_MIN_LENGTH = 1
    MESSAGE_MAX_LENGTH = 4000
    MAX_CONVERSATION_HISTORY = 20  # Keep last 20 messages for context
    
    # Temperature range
    TEMPERATURE_MIN = 0.0
    TEMPERATURE_MAX = 2.0
    TEMPERATURE_STEP = 0.1
    
    # Token range
    TOKENS_MIN = 100
    TOKENS_MAX = 4096
    TOKENS_STEP = 100
    
    # Status codes
    STATUS_ACTIVE = "active"
    STATUS_INACTIVE = "inactive"
    
    # File formats
    CHAT_FILE_EXTENSION = ".json"
    EXPORT_FILE_EXTENSION = ".txt"
    
    # Date formats
    DATE_FORMAT = "%Y-%m-%d"
    DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
    TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

# Theme configuration
class ThemeConfig:
    """Theme and styling configuration"""
    
    # Color schemes
    COLORS = {
        'dark': {
            'primary': '#4361ee',
            'secondary': '#3a0ca3',
            'success': '#4cc9f0',
            'danger': '#f72585',
            'warning': '#f8961e',
            'info': '#7209b7',
            'light': '#f8f9fa',
            'dark': '#212529',
            'background': '#1a1a2e',
            'sidebar': '#16213e',
            'card': '#0f3460',
            'text': '#ffffff',
            'muted': '#6c757d'
        },
        'light': {
            'primary': '#4361ee',
            'secondary': '#3a0ca3',
            'success': '#4cc9f0',
            'danger': '#f72585',
            'warning': '#f8961e',
            'info': '#7209b7',
            'light': '#f8f9fa',
            'dark': '#212529',
            'background': '#ffffff',
            'sidebar': '#f8f9fa',
            'card': '#ffffff',
            'text': '#212529',
            'muted': '#6c757d'
        }
    }
    
    # Font settings
    FONT_FAMILY = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    FONT_SIZE_BASE = '16px'
    
    # Spacing
    SPACING_UNIT = '0.5rem'
    BORDER_RADIUS = '8px'
    
    # Transitions
    TRANSITION_SPEED = '0.3s'
    TRANSITION_TIMING = 'ease-in-out'

# Analytics configuration
class AnalyticsConfig:
    """Analytics and chart configuration"""
    
    # Chart colors
    CHART_COLORS = [
        '#4361ee', '#3a0ca3', '#4cc9f0', '#f72585', 
        '#f8961e', '#7209b7', '#38b000', '#9d4edd'
    ]
    
    # Time periods
    DEFAULT_DAYS_BACK = 7
    STATS_REFRESH_INTERVAL = 30000  # 30 seconds
    
    # Chart options
    CHART_OPTIONS = {
        'responsive': True,
        'maintainAspectRatio': False,
        'plugins': {
            'legend': {
                'position': 'bottom',
                'labels': {
                    'padding': 20,
                    'usePointStyle': True
                }
            }
        }
    }

# Validation patterns
class ValidationPatterns:
    """Regex patterns for validation"""
    
    # Bot name: letters, numbers, spaces, hyphens, underscores
    BOT_NAME = r'^[a-zA-Z0-9 _-]+$'
    
    # GitHub repository name: lowercase letters, numbers, hyphens
    REPO_NAME = r'^[a-z0-9_-]+$'
    
    # API key pattern (basic validation)
    API_KEY = r'^[a-zA-Z0-9_-]{20,}$'

# Error messages
class ErrorMessages:
    """Standard error messages"""
    
    # API errors
    API_KEY_MISSING = "API key is required"
    API_KEY_INVALID = "Invalid API key"
    API_RATE_LIMITED = "Rate limit exceeded. Please try again later."
    API_SERVER_ERROR = "DeepSeek API server error"
    API_NETWORK_ERROR = "Network error. Please check your connection."
    
    # Bot errors
    BOT_NOT_FOUND = "Bot not found"
    BOT_NAME_EXISTS = "A bot with this name already exists"
    BOT_NAME_INVALID = "Bot name can only contain letters, numbers, spaces, hyphens, and underscores"
    BOT_INACTIVE = "Bot is inactive"
    
    # Chat errors
    MESSAGE_EMPTY = "Message cannot be empty"
    MESSAGE_TOO_LONG = "Message is too long (max 4000 characters)"
    
    # GitHub errors
    GITHUB_TOKEN_MISSING = "GitHub token is required"
    REPO_NAME_INVALID = "Repository name can only contain lowercase letters, numbers, hyphens, and underscores"
    REPO_CREATE_FAILED = "Failed to create repository"
    
    # General errors
    VALIDATION_ERROR = "Validation error"
    SERVER_ERROR = "Internal server error"
    PERMISSION_DENIED = "Permission denied"

# Success messages
class SuccessMessages:
    """Standard success messages"""
    
    # Bot operations
    BOT_CREATED = "Bot created successfully"
    BOT_UPDATED = "Bot updated successfully"
    BOT_DELETED = "Bot deleted successfully"
    BOT_TOGGLED = "Bot status updated"
    
    # Chat operations
    CHAT_CLEARED = "Chat cleared successfully"
    CHAT_EXPORTED = "Chat exported successfully"
    
    # GitHub operations
    REPO_CREATED = "Repository created successfully"
    FILES_PUSHED = "Files pushed to GitHub successfully"
    
    # Settings operations
    SETTINGS_SAVED = "Settings saved successfully"
    DATA_EXPORTED = "Data exported successfully"
    DATA_IMPORTED = "Data imported successfully"
    DATA_CLEARED = "All data cleared successfully"

# Default values
class Defaults:
    """Default values for various settings"""
    
    # Bot defaults
    DEFAULT_BOT_NAME = "New Bot"
    DEFAULT_SYSTEM_PROMPT = "You are a helpful AI assistant. Provide clear, concise, and accurate responses."
    
    # Settings defaults
    DEFAULT_THEME = "dark"
    DEFAULT_API_MODEL = "deepseek-chat"
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_MAX_TOKENS = 2048
    
    # Chat defaults
    DEFAULT_USER_NAME = "User"
    DEFAULT_BOT_NAME = "Assistant"

# Environment variable mappings
ENV_VARS = {
    'DEEPSEEK_API_KEY': 'DEEPSEEK_API_KEY',
    'GITHUB_TOKEN': 'GITHUB_TOKEN',
    'FLASK_ENV': 'FLASK_ENV',
    'FLASK_DEBUG': 'FLASK_DEBUG',
    'SECRET_KEY': 'SECRET_KEY'
}

def get_env_var(key: str, default: str = '') -> str:
    """Get environment variable with fallback"""
    return os.environ.get(ENV_VARS.get(key, key), default)

# Initialize default files if they don't exist
def initialize_data_files():
    """Initialize data files with default structure"""
    
    # Create bots.json if it doesn't exist
    if not BOTS_FILE.exists():
        BOTS_FILE.write_text('{"bots": [], "next_id": 1}')
    
    # Create .gitignore in data directory
    gitignore = DATA_DIR / ".gitignore"
    if not gitignore.exists():
        gitignore.write_text("# Git ignore for data directory\n*\n!.gitignore\n")

# Call initialization
initialize_data_files()