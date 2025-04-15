"""
Initialize language models for agent modules.

This module provides centralized initialization of language models
used across different agent implementations to ensure consistent
configuration and efficient resource usage.
"""

from langchain_openai import ChatOpenAI
from openai import OpenAI
from src.core.config import settings

class LLM(ChatOpenAI):
    def __init__(self, **kwargs):
        super().__init__(
            model=settings.chat_completion_model,
            openai_api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            streaming=True
        )

class whisper():
    def __init__(self, **kwargs):
        self.client = OpenAI(
            api_key = settings.openai_api_key,
            base_url = settings.openai_base_url
        )
        
    def transcribe(self, filepath):
        with open(filepath, "rb") as audio_file:
            transcription = self.client.audio.transcriptions.create(
                model=settings.whisper_model,
                file=audio_file,
                response_format="text",
                language="en"
            )
        return transcription

llms = {
    "chat_completion": LLM(),
    "whisper": whisper()
}
