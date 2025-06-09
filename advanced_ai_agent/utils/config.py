"""
Configuration management for the agent system.
"""

import os
import json
from typing import Dict, Any, Optional, List
from pathlib import Path


class Config:
    """
    Configuration manager for the agent system.
    """
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.path.expanduser("~/.agent_config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        
        # Return default configuration
        return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "agent": {
                "max_steps": 15,
                "verbose": False,
                "timeout": 30
            },
            "ai": {
                "provider": "auto",
                "model": "default",
                "temperature": 0.7,
                "max_tokens": 1000
            },
            "tools": {
                "enabled_categories": ["System", "Files", "Web", "Development"],
                "disabled_tools": [],
                "custom_tools": []
            },
            "output": {
                "rich_formatting": True,
                "log_level": "info",
                "save_logs": False,
                "log_file": "agent.log"
            },
            "security": {
                "allow_system_commands": True,
                "allow_file_operations": True,
                "allow_network_access": True,
                "restricted_paths": ["/etc", "/sys", "/proc"],
                "max_file_size": 10485760  # 10MB
            },
            "memory": {
                "max_items": 50,
                "auto_save": False,
                "save_file": "agent_memory.json"
            }
        }
    
    def save_config(self):
        """Save current configuration to file."""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except IOError as e:
            print(f"Warning: Could not save config file: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """Set a configuration value using dot notation."""
        keys = key.split('.')
        config = self.config
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set the value
        config[keys[-1]] = value
    
    def update(self, updates: Dict[str, Any]):
        """Update configuration with a dictionary of changes."""
        for key, value in updates.items():
            self.set(key, value)
    
    def reset_to_defaults(self):
        """Reset configuration to defaults."""
        self.config = self._get_default_config()
    
    def get_agent_config(self) -> Dict[str, Any]:
        """Get agent-specific configuration."""
        return self.config.get("agent", {})
    
    def get_ai_config(self) -> Dict[str, Any]:
        """Get AI-specific configuration."""
        return self.config.get("ai", {})
    
    def get_tools_config(self) -> Dict[str, Any]:
        """Get tools-specific configuration."""
        return self.config.get("tools", {})
    
    def get_output_config(self) -> Dict[str, Any]:
        """Get output-specific configuration."""
        return self.config.get("output", {})
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security-specific configuration."""
        return self.config.get("security", {})
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory-specific configuration."""
        return self.config.get("memory", {})
    
    def is_tool_enabled(self, tool_name: str) -> bool:
        """Check if a specific tool is enabled."""
        disabled_tools = self.get("tools.disabled_tools", [])
        return tool_name not in disabled_tools
    
    def is_category_enabled(self, category: str) -> bool:
        """Check if a tool category is enabled."""
        enabled_categories = self.get("tools.enabled_categories", [])
        return category in enabled_categories
    
    def is_path_restricted(self, path: str) -> bool:
        """Check if a path is restricted."""
        restricted_paths = self.get("security.restricted_paths", [])
        abs_path = os.path.abspath(path)
        
        for restricted in restricted_paths:
            if abs_path.startswith(restricted):
                return True
        
        return False
    
    def get_max_file_size(self) -> int:
        """Get maximum allowed file size."""
        return self.get("security.max_file_size", 10485760)
    
    def export_config(self, file_path: str):
        """Export configuration to a specific file."""
        with open(file_path, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def import_config(self, file_path: str):
        """Import configuration from a file."""
        with open(file_path, 'r') as f:
            imported_config = json.load(f)
        
        # Merge with current config
        self._deep_merge(self.config, imported_config)
    
    def _deep_merge(self, base: Dict[str, Any], update: Dict[str, Any]):
        """Deep merge two dictionaries."""
        for key, value in update.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value
    
    def validate_config(self) -> tuple[bool, List[str]]:
        """Validate the current configuration."""
        errors = []
        
        # Validate agent config
        max_steps = self.get("agent.max_steps")
        if not isinstance(max_steps, int) or max_steps <= 0:
            errors.append("agent.max_steps must be a positive integer")
        
        # Validate AI config
        provider = self.get("ai.provider")
        if provider not in ["auto", "openai", "anthropic"]:
            errors.append("ai.provider must be one of: auto, openai, anthropic")
        
        # Validate tools config
        enabled_categories = self.get("tools.enabled_categories")
        if not isinstance(enabled_categories, list):
            errors.append("tools.enabled_categories must be a list")
        
        # Validate security config
        max_file_size = self.get("security.max_file_size")
        if not isinstance(max_file_size, int) or max_file_size <= 0:
            errors.append("security.max_file_size must be a positive integer")
        
        return len(errors) == 0, errors
    
    def __str__(self) -> str:
        """String representation of the configuration."""
        return json.dumps(self.config, indent=2)
    
    def __repr__(self) -> str:
        """Representation of the configuration."""
        return f"Config(file='{self.config_file}')"