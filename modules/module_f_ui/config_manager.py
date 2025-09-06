"""
Configuration Manager for Module F
Handles YAML configuration loading and module endpoint management.
"""

import yaml
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ModuleConfig:
    """Configuration for a single module."""
    name: str
    url: str
    port: int
    enabled: bool = True


class ConfigManager:
    """Manages configuration loading and module endpoints."""
    
    def __init__(self, config_path: str = "config/modules.yaml"):
        self.config_path = config_path
        self.modules: Dict[str, ModuleConfig] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from YAML file."""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    config_data = yaml.safe_load(f)
                    self._parse_modules(config_data.get('modules', {}))
            else:
                # Use default configuration
                self._load_default_config()
        except Exception as e:
            print(f"Warning: Could not load config from {self.config_path}: {e}")
            self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default module configuration."""
        default_modules = {
            'core': ModuleConfig('Core Intelligence', 'http://localhost', 8001),
            'rag': ModuleConfig('Knowledge Vault', 'http://localhost', 8002),
            'agents': ModuleConfig('Proactive Agents', 'http://localhost', 8003),
            'execution': ModuleConfig('Safe Execution', 'http://localhost', 8004),
            'hybrid': ModuleConfig('Hybrid Gateway', 'http://localhost', 8005)
        }
        self.modules = default_modules
    
    def _parse_modules(self, modules_config: Dict[str, Any]) -> None:
        """Parse modules from configuration data."""
        for key, config in modules_config.items():
            self.modules[key] = ModuleConfig(
                name=config.get('name', key.title()),
                url=config.get('url', 'http://localhost'),
                port=config.get('port', 8000),
                enabled=config.get('enabled', True)
            )
    
    def get_module_url(self, module_key: str) -> Optional[str]:
        """Get full URL for a module."""
        if module_key in self.modules and self.modules[module_key].enabled:
            module = self.modules[module_key]
            return f"{module.url}:{module.port}"
        return None
    
    def get_enabled_modules(self) -> Dict[str, ModuleConfig]:
        """Get all enabled modules."""
        return {k: v for k, v in self.modules.items() if v.enabled}
    
    def is_module_enabled(self, module_key: str) -> bool:
        """Check if a module is enabled."""
        return module_key in self.modules and self.modules[module_key].enabled


# Global config manager instance
config_manager = ConfigManager()