"""
Configuration management for Interlevel POC
Uses environment variables with sensible defaults
"""
import os
from pathlib import Path
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    # Project paths
    BASE_DIR: Path = Path(__file__).parent.parent
    GENERATED_AGENTS_DIR: str = "agents/generated"
    REQUIREMENTS_DIR: str = "data/requirements"
    LOGS_DIR: str = "data/logs"

    # Database
    DATABASE_URL: str = "sqlite:///data/interlevel.db"

    # LLM Provider Configuration
    LLM_PROVIDER: str = Field(
        default="ollama",
        description="LLM provider: ollama, openai, anthropic"
    )

    # Ollama settings
    OLLAMA_HOST: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "codellama"

    # OpenAI settings (optional)
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"

    # Anthropic settings (optional)
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"

    # API Configuration
    API_PORT: int = 5000
    API_HOST: str = "0.0.0.0"
    SECRET_KEY: str = "dev-secret-change-in-production"

    # Agent execution limits
    MAX_EXECUTION_TIME: int = 300  # seconds
    DEFAULT_TOKEN_BUDGET: int = 10000
    MAX_RETRIES: int = 3

    # Logging
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

    def get_absolute_path(self, relative_path: str) -> Path:
        """Convert relative path to absolute based on BASE_DIR"""
        return self.BASE_DIR / relative_path

    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        dirs = [
            self.GENERATED_AGENTS_DIR,
            self.REQUIREMENTS_DIR,
            self.LOGS_DIR,
            "data"
        ]
        for dir_path in dirs:
            path = self.get_absolute_path(dir_path)
            path.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()
