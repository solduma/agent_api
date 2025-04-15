"""
A Streamlit-based playground for testing FastAPI LangGraph Agent endpoints.

This module provides a web interface for interacting with FastAPI endpoints, supporting both
chat-based interactions and file uploads. It dynamically loads API routes from a FastAPI
application and renders appropriate interfaces based on the endpoint type.

Key Features:
- Dynamic route loading from FastAPI application
- Chat interface for text-based endpoints
- File upload interface for file-based endpoints
- Support for streaming responses
- Error handling and response display

The module uses Streamlit for the frontend interface and makes HTTP requests to a local
FastAPI server. It supports various content types and handles both synchronous and
streaming responses.

Dependencies:
    - streamlit
    - requests
    - fastapi
    - logging
    - typing

Configuration:
    API_BASE_URL: Base URL for the FastAPI server (default: "http://localhost:8000")
    AUDIO_EXTENSIONS: Supported audio file extensions
    CONTENT_TYPES: Mapping of content types for file handling
"""

import logging
from typing import Any

import requests
import streamlit as st
from fastapi import UploadFile
from fastapi.openapi.utils import get_openapi

from src.main import app

# Configuration
API_BASE_URL = "http://localhost:8000"
logging.basicConfig(level=logging.INFO)

# File handling constants
AUDIO_EXTENSIONS = (".mp3", ".wav", ".m4a")
CONTENT_TYPES = {"audio": "audio/mpeg", "default": "application/octet-stream"}


def load_routes() -> dict[str, Any]:
    """
    Dynamically load API specifications from main FastAPI app.

    Returns:
        dictionary mapping endpoint paths to route configuration dictionaries.
        Each route configuration contains method, input type, description, etc.

    """
    try:
        logging.info("Loading routes from FastAPI application")

        # Generate OpenAPI specs
        openapi_schema = get_openapi(
            title=app.title, version=app.version, routes=app.routes, description=app.description
        )

        # Convert OpenAPI specs to route configuration
        routes: dict[str, Any] = {}
        for path, path_item in openapi_schema["paths"].items():
            for method, operation in path_item.items():
                route_config = create_route_config(path, method, operation)
                routes[route_config["endpoint"]] = route_config

        logging.info(f"Successfully loaded {len(routes)} routes")
        return routes

    except ImportError as e:
        logging.error(f"Failed to import FastAPI app: {str(e)}")
        return {}
    except Exception as e:
        logging.error(f"Error loading routes: {str(e)}")
        return {}


def create_route_config(path: str, method: str, operation: dict[str, Any]) -> dict[str, Any]:
    """
    Create route configuration from OpenAPI operation data.

    Args:
        path: API endpoint path
        method: HTTP method (get, post, etc.)
        operation: OpenAPI operation object

    Returns:
        Route configuration dictionary

    """
    # Basic route info
    route_config = {
        "endpoint": path,
        "method": method.upper(),
        "input_type": "none",
        "description": operation.get("summary", "No description"),
        "accepted_files": [],
        "required_params": [],
    }

    # Check for path/query parameters
    if "parameters" in operation:
        route_config["required_params"] = [
            param["name"] for param in operation["parameters"] if param.get("required", False)
        ]

    # Determine input type and accepted files
    if "requestBody" in operation:
        content = operation["requestBody"]["content"]
        if "multipart/form-data" in content:
            route_config["input_type"] = "file"
            schema = content["multipart/form-data"].get("schema", {})
            if "properties" in schema:
                file_props = [
                    prop
                    for prop, details in schema["properties"].items()
                    if details.get("type") == "string" and details.get("format") == "binary"
                ]
                route_config["accepted_files"] = file_props if file_props else ["*"]
        else:
            route_config["input_type"] = "text"

    return route_config


def render_chat_interface() -> None:
    """Render the chat interface for text-based API endpoints."""
    st.markdown("### Chat with AI Assistant")

    # Initialize chat history in session state
    initialize_chat_history()

    # Create and display chat container
    chat_container = create_chat_container()

    # Handle user input
    handle_user_input(chat_container)


def initialize_chat_history() -> None:
    """Initialize the chat history in session state if it doesn't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add a welcome message
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": "Hello! I'm your AI assistant. How can I help you today?",
            }
        )


def create_chat_container() -> st.container:
    """
    Create and populate the chat container with message history.

    Returns:
        Streamlit container for chat messages

    """
    chat_container = st.container()

    # Display chat history in the container
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    return chat_container


def handle_user_input(chat_container: st.container) -> None:
    """
    Process user input and get AI response.

    Args:
        chat_container: Streamlit container for displaying chat messages

    """
    # Chat input at the bottom
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})

        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)

        # Get AI response
        get_ai_response(prompt, chat_container)


def get_ai_response(prompt: str, chat_container: st.container) -> None:
    """
    Send request to AI API and handle streaming response.

    Args:
        prompt: User's text input
        chat_container: Streamlit container for displaying chat messages

    """
    url = f"{API_BASE_URL}/chat"

    try:
        with st.spinner("AI is thinking..."):
            response = requests.post(url, json={"message": prompt}, stream=True)

        if response.status_code == requests.codes.ok:
            process_streaming_response(response, chat_container)
        else:
            st.error(f"Failed to get response from AI. Status code: {response.status_code}")
    except requests.exceptions.ConnectionError:
        st.error(f"Connection error: Could not connect to {url}. Is the API server running?")
    except Exception as e:
        st.error(f"Error: {str(e)}")


def parse_sse_line(line: bytes) -> str:
    """
    Parse a single SSE line and extract the message content.

    Args:
        line: Raw bytes from the SSE stream

    Returns:
        Extracted message content or empty string if line is invalid

    """
    try:
        if not line:
            return "  \n\n"

        decoded_line = line.decode("utf-8")
        parts = decoded_line.split(": ", 1)

        if len(parts) > 1 and parts[0] == "data":
            return parts[1]
        return ""
    except Exception as e:
        logging.warning(f"Error parsing SSE line: {str(e)}")
        return ""


def process_streaming_response(response: requests.Response, chat_container: st.container) -> None:
    """
    Process streaming response from AI API.

    Args:
        response: Streaming response from requests
        chat_container: Streamlit container for displaying chat messages

    """
    with chat_container:
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            ai_message = ""

            try:
                for i, line in enumerate(response.iter_lines()):
                    if i % 2 == 0:  # Process every other line as per SSE format
                        message_content = parse_sse_line(line)
                        if message_content:
                            ai_message += message_content
                            message_placeholder.markdown(ai_message)

                # Add complete message to chat history
                if ai_message:
                    st.session_state.messages.append({"role": "assistant", "content": ai_message})
                else:
                    st.warning("Received empty response from AI")
            except Exception as e:
                logging.error(f"Error processing streaming response: {str(e)}")
                st.error("An error occurred while processing the AI response")


def render_file_upload(route_info: dict[str, Any]) -> UploadFile:
    """
    Render file upload widget and handle file processing.

    Args:
        route_info: dictionary containing route configuration

    Returns:
        fastapi.UploadFile instance or None if no file uploaded

    """
    uploaded_file = st.file_uploader("Upload file", type=route_info["accepted_files"])
    upload_file_instance = None
    if uploaded_file:
        # Create a fastapi.UploadFile instance
        upload_file_instance = UploadFile(filename=uploaded_file.name, file=uploaded_file)
    return upload_file_instance


# Initialize routes at module level
REGISTERED_ROUTES = load_routes()


def main() -> None:
    """Render the Streamlit interface."""
    st.title("FastAPI LangGraph Agent Tester")

    # Check if routes were loaded successfully
    if not REGISTERED_ROUTES:
        st.warning(
            "No API routes were found. Make sure the FastAPI application is properly configured."
        )
        return

    # Select endpoint
    selected_route = st.selectbox(
        "Select API Endpoint",
        options=list(REGISTERED_ROUTES.keys()),
    )

    # Handle case where no route is selected
    if not selected_route:
        st.info("Please select an API endpoint to test.")
        return

    route_info = REGISTERED_ROUTES[selected_route]

    # Display route information
    st.write(f"**Method:** {route_info['method']}")
    st.write(f"**Description:** {route_info['description']}")

    # Handle input based on route type
    files = None

    if route_info["input_type"] == "file":
        files = render_file_upload(route_info)
    elif route_info["input_type"] == "text":
        render_chat_interface()
        return

    # Send request button
    if st.button("Send Request"):
        handle_api_request(route_info, files)


def get_content_type(filename: str) -> str:
    """Determine content type based on file extension."""
    return (
        CONTENT_TYPES["audio"] if filename.endswith(AUDIO_EXTENSIONS) else CONTENT_TYPES["default"]
    )


def handle_api_request(route_info: dict[str, Any], files: UploadFile | None) -> None:
    """
    Handle API requests with proper error handling and response display.

    Args:
        route_info: Dictionary containing route configuration including endpoint and method
        files: Optional UploadFile instance for file upload requests

    Returns:
        None. Displays response or error message via Streamlit

    """
    try:
        url = f"{API_BASE_URL}{route_info['endpoint']}"

        with st.spinner("Processing request..."):
            response = make_api_request(url, route_info["method"], files)

        display_response(response)

    except requests.exceptions.RequestException as e:
        st.error(f"Error making request: {str(e)}")
    except Exception as e:
        st.error(f"Unexpected error: {str(e)}")
    finally:
        if files and hasattr(files.file, "close"):
            files.file.close()


def make_api_request(url: str, method: str, files: UploadFile | None) -> requests.Response:
    """Handle API requests with proper error handling."""
    if method == "GET":
        return requests.get(url)
    elif method == "POST":
        files_dict = prepare_files_dict(files) if files else None
        return requests.post(url, files=files_dict)
    else:
        raise ValueError(f"Unsupported method: {method}")


def prepare_files_dict(files: UploadFile) -> dict[str, tuple]:
    """Prepare files dictionary for multipart/form-data request."""
    files.file.seek(0)
    return {"audio_file": (files.filename, files.file.read(), get_content_type(files.filename))}


def display_response(response: requests.Response) -> None:
    """Display API response with proper formatting."""
    st.subheader("Response")
    st.write(f"Status Code: {response.status_code}")

    try:
        response_json = response.json()
        st.json(response_json)
    except Exception:
        st.text(response.text)


if __name__ == "__main__":
    main()
