import streamlit as st 
from src.ui.config import Config
import os


class Layout:
    def __init__(self):
        self.config = Config()
        self.user_selections = {}

    def render(self):
        st.set_page_config(page_title=self.config.get_page_title(), page_icon=":robot_face:", layout="wide")
        st.title(self.config.get_page_title())

        with st.sidebar:
            # Get the options
            self.user_selections["llm_model"] = st.selectbox("Select LLM Model", self.config.get_llm_models())
            self.user_selections["use_case"] = st.selectbox("Select Use Case", self.config.get_use_cases())

            # Get the model based on the LLM model selected
            if self.user_selections["llm_model"] == "Gemini":
                self.user_selections["gemini_model"] = st.selectbox("Select Gemini Model", self.config.get_gemini_models())

            if self.user_selections["llm_model"] == "Groq":
                self.user_selections["groq_model"] = st.selectbox("Select Groq Model", self.config.get_groq_models())
                        
            if self.user_selections["llm_model"] == "OpenAI":
                self.user_selections["openai_model"] = st.selectbox("Select OpenAI Model", self.config.get_openai_models())
            
            # Get API Key and validate it
            self.user_selections["llm_api_key"] = st.text_input("Enter your API key", type="password", key="api_key")
            if self.user_selections["llm_api_key"] == "":
                st.error("Please enter your API key")
            else:
                st.success("API key validated successfully")

            # Get the tool api key (Tavily)
            if self.user_selections["use_case"] == "Chatbot with Web Search" or self.user_selections["use_case"] == "AI News Summarizer":
                os.environ["TAVILY_API_KEY"] = st.text_input("Enter your Tavily API key", type="password", key="tavily_api_key")
                if os.environ["TAVILY_API_KEY"] == "":
                    st.error("Please enter your Tavily API key")
                else:
                    st.success("Tavily API key validated successfully")

            if self.user_selections["use_case"] == "AI News Summarizer":
                st.subheader("AI News Summarizer")
                with st.sidebar:
                    time_frame = st.selectbox("Select Time Frame", ["Daily", "Weekly", "Monthly"], index=0)
                if st.button("Fetch Latest AI News", use_container_width=True):
                    st.session_state.time_frame = time_frame
            
            if st.button("Clear Chat History"):
                st.session_state.messages = []
                st.rerun()

        return self.user_selections