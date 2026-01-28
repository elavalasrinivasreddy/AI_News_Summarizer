from langgraph.graph import StateGraph, START, END
from src.workflow.states.chatbot_with_tools_state import Chatbot_with_tools_state
from src.workflow.nodes.chatbot_with_tools_node import Chatbot_with_tools_node


class Chatbot_with_tools_graph:
    def __init__(self, model):
        self.model = model
        self.graph = StateGraph(Chatbot_with_tools_state)

    def build_graph(self):
        """
        This function builds the graph for the chatbot with tools.
        """
        self.chatbot_with_tools_node = Chatbot_with_tools_node(self.model)
        self.graph.add_node("chatbot_with_tools", self.chatbot_with_tools_node.process)
        self.graph.add_edge(START, "chatbot_with_tools")
        self.graph.add_edge("chatbot_with_tools", END)
        return self.graph.compile()