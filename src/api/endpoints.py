"""
FastAPI router endpoints for meeting minutes generation and chat functionality.

This module provides API endpoints for:
- Processing audio recordings to generate meeting minutes
- Handling chat interactions with a chatbot agent

The endpoints support:
- Audio file upload and processing (.mp3, .wav, .m4a formats)
- Real-time chat interactions with configurable thread management
- Streaming responses for chat functionality
"""

import tempfile
from http import HTTPStatus
from pathlib import Path
from typing import Annotated

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from src.agent.chatbot import ChatbotAgent
from src.agent.minute_writer import process_meeting_recording

from .schemas import AgentResponse

router = APIRouter()


@router.post("/minute-writer/process", response_model=AgentResponse)
async def process_meeting(audio_file: UploadFile) -> AgentResponse:
    """
    Process an uploaded audio file to generate meeting minutes.

    Args:
        audio_file (UploadFile): The uploaded audio file to process.

    Returns:
        MinuteAgentResponse: Response object containing the generated meeting minutes.

    Raises:
        HTTPException: If file format is unsupported or processing fails.

    """
    if not audio_file.filename.lower().endswith((".mp3", ".wav", ".m4a")):
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Unsupported file format. Please upload MP3, WAV, or M4A files.",
        )

    try:
        # Create a temporary file to store the uploaded audio
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=Path(audio_file.filename).suffix
        ) as temp_file:
            # Write uploaded file content to temporary file
            content = await audio_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Process the audio file
        summary = process_meeting_recording(temp_file_path)

        # Clean up the temporary file
        Path(temp_file_path).unlink()

        return AgentResponse(
            success=True,
            message="Meeting minutes generated successfully",
            data={"summary": summary},
        )

    except (ValueError, FileNotFoundError) as e:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}"
        ) from e


@router.post("/chat")
async def chat(
    query: Annotated[dict[str, str], "The message"],
    thread_id: Annotated[str, "Identifier for the chat thread"] = "1",
) -> StreamingResponse:
    """
    Process a chat query and return a response using the ChatbotAgent.

    Returns:
        StreamingResponse: A streaming response containing the chatbot's messages

    Raises:
        HTTPException: If an error occurs during processing

    """
    try:
        config = {"configurable": {"thread_id": thread_id}}
        agent = ChatbotAgent()

        return StreamingResponse(
            agent.stream_chatbot(query, config), media_type="text/event-stream"
        )

    except Exception as e:
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=f"An error occurred: {str(e)}"
        ) from e
