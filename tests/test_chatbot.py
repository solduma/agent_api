"""Test cases for the chatbot module."""

import pytest

from src.agent.chatbot import ChatbotAgent


@pytest.fixture
def chatbot() -> ChatbotAgent:
    """Fixture to create a ChatBot instance for testing."""
    return ChatbotAgent()


def test_chatbot_initialization(chatbot: ChatbotAgent) -> None:
    """Test if ChatBot is initialized correctly."""
    assert isinstance(chatbot, ChatbotAgent)


def test_chatbot_attributes(chatbot: ChatbotAgent) -> None:
    """Test if ChatBot has the required attributes."""
    assert hasattr(chatbot, "llm")
