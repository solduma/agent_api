"""
FastAPI LangGraph Agent Application.

This module implements a FastAPI application that serves as the main entry point
for the LangGraph Agent service. It sets up the FastAPI application, includes API routes,
and provides a basic health check endpoint.

The application uses FastAPI for handling HTTP requests and integrates with
the Anthropic SDK for AI capabilities.
"""

from fastapi import FastAPI

from src.api.endpoints import router

app = FastAPI()

# Include API routes
app.include_router(router)


@app.get("/")
async def root() -> dict[str, str]:
    """
    Return a welcome message for the root endpoint.

    Returns:
        dict[str, str]: A dictionary containing a welcome message.

    """
    return {"message": "Welcome to the FastAPI LangGraph Agent!"}
