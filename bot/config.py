"""Bot configuration loaded from environment variables."""

import os
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Bot configuration settings."""

    # Telegram
    bot_token: str = Field(default="", alias="BOT_TOKEN")

    # LMS API
    lms_api_base_url: str = Field(default="", alias="LMS_API_BASE_URL")
    lms_api_key: str = Field(default="", alias="LMS_API_KEY")

    # LLM API
    llm_api_key: str = Field(default="", alias="LLM_API_KEY")
    llm_api_base_url: str = Field(default="", alias="LLM_API_BASE_URL")
    llm_api_model: str = Field(default="qwen3-coder-plus", alias="LLM_API_MODEL")

    model_config = SettingsConfigDict(
        env_file=".env.bot.secret",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )


def load_config() -> BotSettings:
    """Load configuration from environment or .env.bot.secret file."""
    # Check for .env.bot.secret in the bot directory
    bot_dir = Path(__file__).resolve().parent
    env_file = bot_dir / ".env.bot.secret"

    if env_file.exists():
        return BotSettings(_env_file=env_file)

    # Fall back to environment variables only
    return BotSettings.model_validate({})


settings = load_config()
