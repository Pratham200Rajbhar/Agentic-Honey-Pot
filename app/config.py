"""
Configuration management for Agentic Honey-Pot API
"""

import os
from functools import lru_cache
from typing import Set

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self):
        self.api_keys: Set[str] = self._parse_api_keys()
        self.environment: str = os.getenv("ENVIRONMENT", "development")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.weights_path: str = os.getenv("WEIGHTS_PATH", "data/weights.json")
        self.debug: bool = self.environment == "development"

    def _parse_api_keys(self) -> Set[str]:
        """Parse API keys from environment variable."""
        keys_str = os.getenv("API_KEYS", "")
        return set(key.strip() for key in keys_str.split(",") if key.strip())

    def is_valid_api_key(self, key: str) -> bool:
        """Validate API key using constant-time comparison."""
        if not key:
            return False
        # Use secrets.compare_digest for timing attack prevention
        import secrets

        for valid_key in self.api_keys:
            if secrets.compare_digest(key, valid_key):
                return True
        return False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
