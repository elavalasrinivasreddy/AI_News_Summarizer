from typing_extensions import TypedDict, List
from typing import Annotated
from langgraph.graph.message import add_messages

class Chatbot_state(TypedDict):
    """
    This class is used to store the state of the chatbot.
    """
    messages: Annotated[List, add_messages] # List of messages
    summary: str # Summary of the news
    news_data: List # List of news data
    frequency: str # Frequency of the news