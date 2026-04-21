"""
GitHub integration utilities for Bot Manager application.
Handles pushing bot configurations to GitHub repositories.
"""

import os
import json
import base64
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import requests
from flask import current_app


class GitHubIntegration:
    """GitHub API integration for pushing bot configurations."""
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub integration.
        
        Args:
            github_token: GitHub personal access token
        """
        self.github_token = github_token or os.getenv('GITHUB_TOKEN')
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
    
    def validate_token(self) -> Tuple[bool, str]:
        """
        Validate GitHub token by making a test API call.
        
        Returns:
            Tuple of (is_valid, message)
        """
        if not self.github_token:
            return False, "GitHub token not configured"
        
        try:
            response = requests.get(
                f"{self.api_base}/user",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                user_data = response.json()
                return True, f"Connected as {user_data.get('login', 'Unknown')}"
            elif response.status_code == 401:
                return False, "Invalid GitHub token"
            else:
                return False, f"GitHub API error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Connection error: {str(e)}"
    
    def validate_repo_name(self, repo_name: str) -> Tuple[bool, str]:
        """
        Validate repository name format.
        
        Args:
            repo_name: Repository name to validate
            
        Returns:
            Tuple of (is_valid, message)
        """
        if not repo_name:
            return False, "Repository name cannot be empty"
        
        # GitHub repo name rules
        if len(repo_name) > 100:
            return False, "Repository name must be 100 characters or less"
        
        # Check for invalid characters
        import re
        if not re.match(r'^[a-zA-Z0-9._-]+$', repo_name):
            return False, "Repository name can only contain letters, numbers, ., -, and _"
        
        # Check for reserved names
        reserved_names = ['.', '..', '.git']
        if repo_name.lower() in reserved_names:
            return False, f"'{repo_name}' is a reserved name"
        
        return True, "Valid repository name"
    
    def create_repository(self, repo_name: str, description: str = "", private: bool = True) -> Tuple[bool, Dict[str, Any]]:
        """
        Create a new GitHub repository.
        
        Args:
            repo_name: Name of the repository
            description: Repository description
            private: Whether repository should be private
            
        Returns:
            Tuple of (success, data)
        """
        if not self.github_token:
            return False, {"error": "GitHub token not configured"}
        
        # Validate repo name
        is_valid, message = self.validate_repo_name(repo_name)
        if not is_valid:
            return False, {"error": message}
        
        try:
            # First check if user exists
            user_response = requests.get(
                f"{self.api_base}/user",
                headers=self.headers,
                timeout=10
            )
            
            if user_response.status_code != 200:
                return False, {"error": "Failed to authenticate with GitHub"}
            
            user_data = user_response.json()
            username = user_data.get('login')
            
            # Check if repo already exists
            check_response = requests.get(
                f"{self.api_base}/repos/{username}/{repo_name}",
                headers=self.headers,
                timeout=10
            )
            
            if check_response.status_code == 200:
                return False, {"error": f"Repository '{repo_name}' already exists"}
            
            # Create repository
            repo_data = {
                "name": repo_name,
                "description": description or "Bot Manager Configuration",
                "private": private,
                "auto_init": True,  # Initialize with README
                "has_issues": True,
                "has_projects": False,
                "has_wiki": False
            }
            
            response = requests.post(
                f"{self.api_base}/user/repos",
                headers=self.headers,
                json=repo_data,
                timeout=30
            )
            
            if response.status_code in [201, 202]:
                repo_info = response.json()
                return True, {
                    "repo_url": repo_info.get("html_url"),
                    "clone_url": repo_info.get("clone_url"),
                    "full_name": repo_info.get("full_name"),
                    "owner": repo_info.get("owner", {}).get("login")
                }
            else:
                error_msg = response.json().get("message", "Unknown error")
                return False, {"error": f"Failed to create repository: {error_msg}"}
                
        except requests.exceptions.RequestException as e:
            return False, {"error": f"GitHub API error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    def push_bot_configuration(self, repo_name: str, bot_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """
        Push bot configuration to GitHub repository.
        
        Args:
            repo_name: Repository name
            bot_data: Bot configuration data
            
        Returns:
            Tuple of (success, data)
        """
        if not self.github_token:
            return False, {"error": "GitHub token not configured"}
        
        try:
            # Get user info
            user_response = requests.get(
                f"{self.api_base}/user",
                headers=self.headers,
                timeout=10
            )
            
            if user_response.status_code != 200:
                return False, {"error": "Failed to authenticate with GitHub"}
            
            user_data = user_response.json()
            username = user_data.get('login')
            
            # Prepare files to push
            files = self._prepare_bot_files(bot_data)
            
            # Create or update files in repository
            results = []
            for file_path, content in files.items():
                success, result = self._create_or_update_file(
                    username, repo_name, file_path, content
                )
                if not success:
                    return False, result
                results.append(result)
            
            return True, {
                "message": f"Successfully pushed {len(files)} files to {repo_name}",
                "repo_url": f"https://github.com/{username}/{repo_name}",
                "files_pushed": list(files.keys())
            }
            
        except requests.exceptions.RequestException as e:
            return False, {"error": f"GitHub API error: {str(e)}"}
        except Exception as e:
            return False, {"error": f"Unexpected error: {str(e)}"}
    
    def _prepare_bot_files(self, bot_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Prepare bot files for GitHub push.
        
        Args:
            bot_data: Bot configuration data
            
        Returns:
            Dictionary of file paths and their content
        """
        files = {}
        
        # Main bot configuration
        if 'bots' in bot_data:
            files['bots.json'] = json.dumps(bot_data['bots'], indent=2)
        
        # Chat history
        if 'chats' in bot_data:
            for bot_id, chat_data in bot_data['chats'].items():
                if chat_data:
                    chat_dir = f"chats/{bot_id}"
                    for chat_file, chat_content in chat_data.items():
                        files[f"{chat_dir}/{chat_file}"] = json.dumps(chat_content, indent=2)
        
        # README with bot information
        readme_content = self._generate_readme(bot_data)
        files['README.md'] = readme_content
        
        # Configuration summary
        config_summary = {
            "export_date": datetime.now().isoformat(),
            "total_bots": len(bot_data.get('bots', [])),
            "total_chats": sum(len(chats) for chats in bot_data.get('chats', {}).values())
        }
        files['config_summary.json'] = json.dumps(config_summary, indent=2)
        
        return files
    
    def _generate_readme(self, bot_data: Dict[str, Any]) -> str:
        """
        Generate README.md content for the repository.
        
        Args:
            bot_data: Bot configuration data
            
        Returns:
            README content as string
        """
        total_bots = len(bot_data.get('bots', []))
        active_bots = sum(1 for bot in bot_data.get('bots', []) if bot.get('active', False))
        
        readme = f"""# Bot Manager Configuration

This repository contains exported bot configurations from Bot Manager.

## Export Information
- **Export Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Bots**: {total_bots}
- **Active Bots**: {active_bots}

## Bot List
"""
        
        for bot in bot_data.get('bots', []):
            readme += f"\n### {bot.get('name', 'Unnamed Bot')}"
            readme += f"\n- **ID**: {bot.get('id', 'N/A')}"
            readme += f"\n- **Status**: {'Active' if bot.get('active') else 'Inactive'}"
            readme += f"\n- **Model**: {bot.get('model', 'deepseek-chat')}"
            readme += f"\n- **Temperature**: {bot.get('temperature', 0.7)}"
            readme += f"\n- **Max Tokens**: {bot.get('max_tokens', 2048)}"
            readme += f"\n- **Created**: {bot.get('created_at', 'N/A')}"
            readme += "\n"
        
        readme += """
## File Structure
- `bots.json` - Main bot configurations
- `chats/` - Directory containing chat histories
- `config_summary.json` - Export metadata

## Importing
To import these configurations back into Bot Manager:
1. Clone this repository
2. Use the Import feature in Bot Manager Settings
3. Select the `bots.json` file

## Notes
- Chat histories are stored in JSON format
- Bot configurations include system prompts and model settings
- This export was generated automatically by Bot Manager
"""
        
        return readme
    
    def _create_or_update_file(self, username: str, repo_name: str, file_path: str, content: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Create or update a file in GitHub repository.
        
        Args:
            username: GitHub username
            repo_name: Repository name
            file_path: Path to file in repository
            content: File content
            
        Returns:
            Tuple of (success, data)
        """
        try:
            # Check if file exists
            check_url = f"{self.api_base}/repos/{username}/{repo_name}/contents/{file_path}"
            check_response = requests.get(check_url, headers=self.headers, timeout=10)
            
            # Prepare file data
            file_data = {
                "message": f"Add/update {file_path} from Bot