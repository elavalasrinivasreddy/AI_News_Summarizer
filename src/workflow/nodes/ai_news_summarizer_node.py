from tavily import TavilyClient
from langchain_core.prompts import ChatPromptTemplate
import os

class AINewsSummarizerNode:
    def __init__(self, model):
        self.model = model
        self.tavily = TavilyClient()
        self.state = {}

    def fetch_ai_news(self, state: dict) -> dict:
        """
        This function fetches the latest AI news from the web.
        """
        # Get the frequency from the last message
        frequency = state["messages"][-1].content.lower()
        if frequency.startswith("fetching "):
            # Extract 'daily', 'weekly', etc. from 'Fetching Daily Latest AI News'
            parts = frequency.split(" ")
            if len(parts) > 1:
                frequency = parts[1].lower()
            
        time_range_map = {"daily": "d", "weekly": "w", "monthly": "m", "yearly": "y"}
        days_map = {"daily": 1, "weekly": 7, "monthly": 30, "yearly": 365}
        
        # Default to daily if not matched
        if frequency not in time_range_map:
            frequency = "daily"

        # Hit the tavily api
        response = self.tavily.search(
            query="latest AI news", 
            topic="news",
            time_range=time_range_map[frequency], 
            include_answer="advanced",
            max_results=10,
            days=days_map[frequency]
        )
        
        return {
            "news_data": response.get('results', []),
            "frequency": frequency
        }

    def summarize_ai_news(self, state: dict) -> dict:
        """
        This function summarizes the latest AI news.
        """
        system_prompt = """
        You are an expert AI news summarizer. Your task is to summarize the latest AI news from the web and provide in markdown format.
        For each item include:
        - Date in dd-mm-yyyy format
        - Title in bold
        - Concise summary of the news
        - URL in markdown format

        Output Format:
        #### [Date] 
        **[Title]**
        - [Summary](URL)
        """
        prompt_template = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Summarize the below latest AI news from the web: \n{articles}")
        ])

        # Get news data from state
        news_data = state.get("news_data", [])
        if not news_data:
            return {"summary": "No news articles found for this period."}

        new_content = "\n\n".join(
            f"content: {news.get('content', '')}\nurl: {news.get('url', '')}\ndate: {news.get('published_date', '')}\ntitle: {news.get('title', '')}" 
            for news in news_data
        )

        # Invoke the model
        response = self.model.invoke(prompt_template.format(articles=new_content))
        return {"summary": response.content}

    def save_ai_results(self, state: dict) -> dict:
        """
        This function saves the AI news results (optional).
        """
        frequency = state.get("frequency", "daily")
        summary = state.get("summary", "")
        
        # Ensure data directory exists
        try:
            if not os.path.exists("../data"):
                os.makedirs("../data")
                
            file_name = f"../data/ai_news_results_{frequency}.md"
            with open(file_name, "w") as f:
                f.write(f"# AI News Results ({frequency.capitalize()})\n\n")
                f.write(summary)
            return {"file_name": file_name}
        except Exception:
            return {}

        