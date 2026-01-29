    from tavily import TavilyClient

class AINewsSummarizerNode:
    def __init__(self, model):
        self.model = model
        self.tavily = TavilyClient()
        self.state = {}

    def fetch_ai_news(self, state:dict) -> dict:
        """
        This function fetches the latest AI news from the web.
        """
        # Get the frequency from the state
        frequency = state["messages"][0].content.lower()
        self.state["frequency"] = frequency
        time_range_map = {"daily": "d", "weekly": "w", "monthly": "m", "yearly": "y"}
        days_map = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}
        
        # Hit the tavily api
        response = self.tavily.search(
            query="latest AI news", 
            topic="technology",
            time_range=time_range_map[frequency], 
            include_answer="advanced",
            max_results=10,
            days=days_map[frequency],
            # include_domains=["techcrunch.com", "wired.com", "theverge.com", "arstechnica.com"]
        )
        state["news_data"] = response.get('results', [])
        self.state["news_data"] = state["news_data"]
        return state