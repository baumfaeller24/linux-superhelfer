"""
Configuration management for Linux Superhelfer modules.
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from shared.models import SystemConfig, ModuleConfig


class ConfigManager:
    """Manages system configuration from YAML files."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self._config = None
    
    def load_config(self) -> SystemConfig:
        """Load configuration from YAML file."""
        if not self.config_path.exists():
            return self._create_default_config()
        
        with open(self.config_path, 'r') as f:
            config_data = yaml.safe_load(f)
        
        return SystemConfig(**config_data)
    
    def _create_default_config(self) -> SystemConfig:
        """Create default configuration."""
        default_modules = {
            "core": ModuleConfig(name="core", port=8001),
            "rag": ModuleConfig(name="rag", port=8002),
            "agents": ModuleConfig(name="agents", port=8003),
            "execution": ModuleConfig(name="execution", port=8004),
            "hybrid": ModuleConfig(name="hybrid", port=8005),
            "ui": ModuleConfig(name="ui", port=8000)
        }
        
        default_features = {
            "voice_enabled": False,
            "auto_escalation": True,
            "safe_mode": True,
            "confidence_threshold": 0.5
        }
        
        default_ollama = {
            "host": "localhost",
            "port": 11434,
            "model": "llama3.1:8b-instruct-q4_0",
            "embedding_model": "nomic-embed-text"
        }
        
        return SystemConfig(
            modules=default_modules,
            features=default_features,
            ollama=default_ollama
        )
    
    def save_config(self, config: SystemConfig):
        """Save configuration to YAML file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(config.dict(), f, default_flow_style=False)


def get_module_url(module_name: str, config: SystemConfig) -> str:
    """Get full URL for a module."""
    module_config = config.modules.get(module_name)
    if not module_config:
        raise ValueError(f"Module {module_name} not found in configuration")
    
    return f"http://{module_config.host}:{module_config.port}"