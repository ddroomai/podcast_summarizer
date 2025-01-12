import os
from pathlib import Path
import logging

class EnvironmentManager:
    """Manages environment-specific configurations."""
    
    def __init__(self):
        self.env = os.getenv('APP_ENV', 'development')
        
    def get_config_path(self) -> Path:
        """Get environment-specific config path."""
        return Path(f"config/{self.env}.yaml")
        
    def is_production(self) -> bool:
        """Check if running in production."""
        return self.env == 'production'
        
    def get_log_level(self) -> str:
        """Get environment-specific log level."""
        return 'INFO' if self.is_production() else 'DEBUG'

async def initialize_system():
    """Initialize system with environment-specific config."""
    env_manager = EnvironmentManager()
    config_path = env_manager.get_config_path()
    
    # Initialize components with config
    summarizer = PodcastSummarizer(config_path)
    
    # Set up logging
    logging.basicConfig(
        level=env_manager.get_log_level(),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    return summarizer