"""
Configuration module for the coder application.

This module defines the application settings using Pydantic BaseSettings.
It includes configuration for:
- Whisper model selection for speech-to-text
- Summary model selection for text processing

The settings can be overridden through environment variables.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings class.

    This class defines the configuration settings for the coder application
    using Pydantic BaseSettings.

    Attributes:
        environment (str): The environment in which the application is running.
            Defaults to "internet". Set to "intranet" for local deployment.
        whisper_model (str): The model name for Whisper speech-to-text processing.
            Defaults to "whisper-v3-large-turbo".
        summary_model (str): The model name for text summarization processing.
            Defaults to "gpt-4o-mini-0125".

    """

    openai_base_url: str
    openai_api_key: str
    whisper_model: str = "gpt-4o-mini-transcribe"
    chat_completion_model: str = "gpt-4o-mini"
    coder_model: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


settings = Settings()
