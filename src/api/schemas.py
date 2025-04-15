"""
Module defines Pydantic models for API response schemas.

Contains:
- AgentResponse: Base response model for all agent operations

The models provide structured response formats with success status,
messages and optional data payloads.
"""

from typing import Annotated, Any

from pydantic import BaseModel


class AgentResponse(BaseModel):
    """
    Base response model for all agent operations.

    Attributes:
        success (bool): Indicates if the operation was successful
        message (str): Response message or description
        data (Optional[dict]): Optional dictionary containing additional response data

    """

    success: bool
    message: str
    data: dict[str, Any] | None = None


class MinuteWriterOutput(BaseModel):
    """
    Output model for MinuteWriter class.

    Attributes:
        audio_path (str): Path to the processed audio file
        transcript (str): Transcribed text from the audio file
        summary (str): Generated summary of the meeting

    """

    audio_path: Annotated[str, "Path to the processed audio file"]
    transcript: Annotated[str, "Transcribed text from the audio file"]
    summary: Annotated[str, "Generated summary of the meeting"]
