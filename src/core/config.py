"""
Configuration module for Remnawave Bot
"""
import os
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # Telegram Configuration
    telegram_bot_token: str
    admin_ids: str
    
    # Remnawave API Configuration
    remnawave_api_url: str
    remnawave_api_token: Optional[str] = None
    remnawave_username: Optional[str] = None
    remnawave_password: Optional[str] = None
    
    # Security
    pin_code: str = "1234"
    
    # Application Configuration
    log_level: str = "INFO"
    debug: bool = False
    
    # Redis Configuration
    redis_url: str = "redis://localhost:6379/0"
    redis_enabled: bool = False
    
    # Bulk Operations
    max_bulk_create: int = 20
    
    @property
    def admin_id_list(self) -> List[int]:
        """Parse admin IDs from comma-separated string"""
        try:
            return [int(id_str.strip()) for id_str in self.admin_ids.split(",") if id_str.strip()]
        except (ValueError, AttributeError):
            return []
    
    @property
    def is_debug(self) -> bool:
        """Check if debug mode is enabled"""
        return self.debug or self.log_level.upper() == "DEBUG"


# Create settings instance
settings = Settings()
