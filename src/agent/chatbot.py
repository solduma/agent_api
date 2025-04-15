"""
Module implementing a chatbot agent using LangChain and OpenAI's ChatGPT.

The module provides a ChatbotAgent class that:
- Initializes a chat model using OpenAI's API
- Sets up a simple graph workflow for processing chat messages
- Handles streaming responses from the chat model
"""

from typing import Annotated

from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel

from src.agent import llms


# Define state with message history
class State(BaseModel):
    """
    State class representing the conversation state.

    Attributes:
        messages (list[Message]): A list of conversation messages annotated with add_messages.

    """

    messages: Annotated[list, add_messages]


class ChatbotAgent:
    """
    A chatbot agent class that handles conversational interactions using LangChain and OpenAI.

    Attributes:
        llm (ChatOpenAI): The language model instance used for chat interactions.
        graph (CompiledGraph): The compiled graph workflow for message processing.
        stream_mode (list): Configuration flags for controlling streaming behavior.

    """

    def __init__(self) -> None:
        """
        Initialize a new ChatbotAgent instance.

        Args:
            stream_mode (list): A list of streaming configuration flags that control
                how the chat responses are streamed.

        """
        self.llm = llms["chat_completion"]

        async def chatbot(state: State) -> dict:
            response = await self.llm.ainvoke(state.messages)
            return {"messages": response}

        # Create graph workflow
        graph_builder = StateGraph(State)
        graph_builder.add_node("chatbot", chatbot)
        graph_builder.set_entry_point("chatbot")
        graph_builder.set_finish_point("chatbot")
        self.graph = graph_builder.compile()

    async def stream_chatbot(
        self,
        query: Annotated[dict[str, str], "The message"],
        config: Annotated[dict[str, dict], "Configuration parameters"],
    ) -> str:
        """
        Stream chat responses from the chatbot asynchronously.

        Returns:
            str: Yields chunks of the chatbot's response as a stream.

        Raises:
            Exception: If any error occurs during the streaming process.

        """
        try:
            human_message = HumanMessage(content=query["message"])

            async for chunk in self.graph.astream(
                input={"messages": [human_message]}, config=config, stream_mode="messages"
            ):
                message, meta = chunk
                yield f"data: {message.content}\n\n"
        except Exception as e:
            yield f"data: {str(e)}\n\n"
