from langgraph.graph import StateGraph, END
from src.workflow.state import ChatbotState
from src.workflow.nodes.ai_news_summarizer_node import AINewsSummarizerNode

class AINewsSummarizerGraph:
    def __init__(self, model):
        self.model = model
        self.graph = StateGraph()
        
    def build_graph(self):
        """
        This function builds the graph for the AI news summarizer.
        """

        # add nodes
        ai_news_summarizer_node = AINewsSummarizerNode(self.model)
        self.graph.add_node("fetch_ai_news", ai_news_summarizer_node.fetch_ai_news)
        self.graph.add_node("summarize_ai_news", ai_news_summarizer_node.summarize_ai_news)
        self.graph.add_node("save_ai_results", ai_news_summarizer_node.save_ai_results)

        # add edges
        self.graph.set_entry_point("fetch_ai_news")
        self.graph.add_edge("fetch_ai_news", "summarize_ai_news")
        self.graph.add_edge("summarize_ai_news", "save_ai_results")
        self.graph.add_edge("save_ai_results", END)
        
        return self.graph.compile()
        