from tavily import TavilyClient
from langchain_community.prompts import ChatPromptTemplate

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

    def summarize_ai_news(self, state:dict) -> dict:
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
        **Title**
        [Summary (URL)]
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("user", "Summarize the below latest AI news from the web: \n{news_data}")
        ])

        # Create new content
        news_data = state["news_data"]
        new_content = "\n\n".join(
            f"content: {news['content']}\nurl: {news['url']}\ndate: {news['published_date']}\ntitle: {news['title']}" for news in news_data
        )

        # Invoke the model
        response = self.model.invoke(prompt.format(news_data=new_content))
        state["summary"] = response.content
        self.state["summary"] = state["summary"]
        return self.state

    def save_ai_results(self, state:dict) -> dict:
        """
        This function saves the AI news results.
        """
        # Save the results to a file
        frequency = self.state["frequency"]
        summary = self.state["summary"]
        file_name = f"./data/ai_news_results_{frequency}.md"
        self.state["file_name"] = file_name 
        with open(file_name, "w") as f:
            f.write(f"# AI News Results ({frequency.capitalize()})\n\n")
            f.write(summary)
        return self.state

        