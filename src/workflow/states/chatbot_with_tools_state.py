from typing_extensions import TypedDict, List
from typing import Annotated
from langgraph.graph.message import add_messages

class Chatbot_with_tools_state(TypedDict): 
    """
    This class is used to store the state of the chatbot with tools.
    """
    messages: Annotated[List, add_messages]
    
    