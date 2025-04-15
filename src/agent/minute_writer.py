"""
MinuteWriter module for processing meeting recordings into transcripts and summaries.

This module provides functionality to:
- Transcribe audio recordings using OpenAI's Whisper model
- Generate structured meeting summaries using GPT-4
- Handle the workflow of audio processing through a graph-based pipeline
"""

from typing import Annotated, Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import Graph, StateGraph
from pydantic import ValidationError

from src.agent import llms
from src.api.schemas import MinuteWriterOutput


class MinuteWriter:
    """
    Core class for processing meeting recordings into transcripts and summaries.

    This class handles:
    - Audio transcription using OpenAI's Whisper model
    - Meeting summarization using GPT-4
    - State management for the processing pipeline

    Methods:
        transcribe: Converts audio to text using OpenAI's Audio API
        summarize: Generates structured meeting summary from transcript

    """

    def __init__(self) -> None:
        """
        Initialize MinuteWriter with required language models.

        Raises:
            RuntimeError: If initialization of language models fails

        """
        try:
            self.whisper = llms["whisper"]
            self.summarizer = llms["chat_completion"]
        except Exception as e:
            raise RuntimeError(f"Failed to initialize MinuteWriter: {str(e)}") from e

    def transcribe(
        self,
        state: Annotated[dict[str, Any], "Current state dictionary containing audio file path"],
    ) -> dict[str, Any]:
        """
        Transcribe audio file to text using OpenAI's Whisper model.

        Args:
            state: Dictionary containing audio file path and other state information

        Returns:
            Updated state dictionary with transcript

        Raises:
            ValueError: If transcription fails
            FileNotFoundError: If audio file is not found

        """
        try:
            state["transcript"] = self.whisper.transcribe(state["audio_path"])
            return state
        except Exception as e:
            raise ValueError(f"Failed to transcribe audio: {str(e)}") from e

    def summarize(self, state: dict[str, Any]) -> dict[str, Any]:
        """
        Generate structured meeting summary from transcript using GPT-4.

        Args:
            state: Dictionary containing transcript and other state information

        Returns:
            Updated state dictionary with meeting summary

        Raises:
            ValueError: If summarization fails or transcript is missing

        """
        try:
            transcript = state["transcript"]
            if not transcript:
                raise ValueError("Missing or empty transcript in state")

            prompt = f"""Please summarize this meeting transcript and format it in markdown:

            {transcript}

            Format the summary with these sections:
            - Meeting Overview
            - Key Points
            - Action Items
            - Next Steps
            """

            ai_message = self.summarizer.invoke(
                input=[
                    SystemMessage(
                        content="""You are a helpful assistant that creates concise
                                   meeting summaries."""
                    ),
                    HumanMessage(content=prompt),
                ],
            )
            state["summary"] = ai_message.content
            MinuteWriterOutput(**state)  # Validate output state
            return state
        except (ValidationError, KeyError, Exception) as e:
            raise ValueError(f"Failed to summarize transcript: {str(e)}") from None


def create_minute_writer_graph() -> Graph:
    """
    Create and configure a workflow graph for the MinuteWriter pipeline.

    Returns:
        Graph: A compiled workflow graph with transcription and summarization nodes
        configured for processing meeting recordings.

    The graph consists of two main nodes:
    - transcribe: Handles audio transcription
    - summarize: Generates meeting summary from transcript

    """
    workflow = StateGraph(state_schema=dict)  # Add state schema

    # Add nodes
    workflow.add_node("transcribe", MinuteWriter().transcribe)
    workflow.add_node("summarize", MinuteWriter().summarize)

    # Create edges
    workflow.add_edge("transcribe", "summarize")
    workflow.set_entry_point("transcribe")
    workflow.set_finish_point("summarize")

    # Compile graph
    graph = workflow.compile()

    return graph


def process_meeting_recording(audio_file_path: str) -> str:
    """
    Process a meeting recording by transcribing and summarizing it.

    Args:
        audio_file_path (str): Path to the audio file to be processed

    Returns:
        str: The generated meeting summary in markdown format

    Raises:
        RuntimeError: If processing fails at any stage

    """
    try:
        graph = create_minute_writer_graph()
        state = {"audio_path": audio_file_path}
        result = graph.invoke(state)
        return result["summary"]
    except Exception as e:
        raise RuntimeError(f"Failed to process meeting recording: {str(e)}") from e
