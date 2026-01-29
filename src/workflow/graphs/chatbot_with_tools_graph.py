from langgraph.graph import StateGraph, START, END
from src.workflow.states.chatbot_state import Chatbot_state
from src.workflow.nodes.chatbot_node import Chatbot_node
from src.workflow.nodes.tools_node import Tools_node
from src.workflow.tools.tools import get_tools
from langgraph.prebuilt import tools_condition

class Chatbot_with_tools_graph:
    def __init__(self, model):
        self.model = model
        self.graph = StateGraph(Chatbot_state)

    def build_graph(self):
        """
        This function builds the graph for the chatbot with tools.
        """
        tools = get_tools()
        # get the chatbot node
        self.model = self.model.bind_tools(tools)
        self.chatbot_node = Chatbot_node(self.model)
        # get the tools node
        self.tools_node = Tools_node(get_tools())

        # add nodes to the graph
        self.graph.add_node("chatbot", self.chatbot_node.process)
        self.graph.add_node("tools", self.tools_node)

        # add edges to the graph
        self.graph.add_edge(START, "chatbot")
        self.graph.add_conditional_edges("chatbot",tools_condition)
        self.graph.add_edge("tools", "chatbot")
        self.graph.add_edge("chatbot", END)
        return self.graph.compile()
