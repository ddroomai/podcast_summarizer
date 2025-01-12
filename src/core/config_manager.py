from typing import Dict, Any, Optional
import yaml
import os
from pathlib import Path
import logging
from dataclasses import dataclass

class ConfigurationError(Exception):
    """Raised when configuration validation fails."""
    pass

@dataclass
class SystemConfig:
    """Core system configuration."""
    # OpenAI settings
    api_key: str
    model_version: str = "gpt-4"
    max_tokens: int = 1000
    temperature: float = 0.3
    
    # Chunking settings
    min_chunk_size: int = 400
    max_chunk_size: int = 1000
    optimal_chunk_size: int = 750
    
    # Processing settings
    context_window_size: int = 3
    similarity_threshold: float = 0.85
    max_retries: int = 3

class ConfigManager:
    """Manages system configuration."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = config_path
        self.logger = logging.getLogger(__name__)
        self.config = self.load_config()
        
    def load_config(self) -> SystemConfig:
        """Load and validate configuration."""
        try:
            # Load base config
            with open(self.config_path) as f:
                config_data = yaml.safe_load(f)
                
            # Load environment variables
            self.load_environment_variables(config_data)
            
            # Validate configuration
            self.validate_config(config_data)
            
            return SystemConfig(**config_data)
            
        except Exception as e:
            self.logger.error(f"Configuration loading failed: {str(e)}")
            raise ConfigurationError(f"Failed to load config: {str(e)}")
            
    def load_environment_variables(self, config: Dict[str, Any]):
        """Load sensitive values from environment variables."""
        env_vars = {
            'api_key': 'OPENAI_API_KEY',
            'model_version': 'OPENAI_MODEL_VERSION'
        }
        
        for config_key, env_var in env_vars.items():
            if env_value := os.getenv(env_var):
                config[config_key] = env_value

class ConfigValidator:
    """Validates configuration values."""
    
    @staticmethod
    def validate_config(config: Dict[str, Any]):
        """Validate configuration values."""
        required_fields = {
            'api_key': str,
            'model_version': str,
            'min_chunk_size': int,
            'max_chunk_size': int
        }
        
        for field, field_type in required_fields.items():
            if field not in config:
                raise ConfigurationError(f"Missing required field: {field}")
            if not isinstance(config[field], field_type):
                raise ConfigurationError(
                    f"Invalid type for {field}. Expected {field_type}"
                )