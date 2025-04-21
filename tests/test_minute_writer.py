"""Test cases for the minute writer module."""

import pytest

from src.agent.minute_writer import MinuteWriter


@pytest.fixture
def minute_writer() -> MinuteWriter:
    """Fixture to create a MinuteWriter instance for testing."""
    return MinuteWriter()


def test_minute_writer_initialization(minute_writer: MinuteWriter) -> None:
    """Test if MinuteWriter is initialized correctly."""
    assert isinstance(minute_writer, MinuteWriter)


def test_minute_writer_attributes(minute_writer: MinuteWriter) -> None:
    """Test if MinuteWriter has the required attributes."""
    assert hasattr(minute_writer, "whisper")
    assert hasattr(minute_writer, "summarizer")
