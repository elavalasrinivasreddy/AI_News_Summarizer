from langchain_google_genai import ChatGoogleGenerativeAI
import os
import streamlit as st

class Gemini_with_tools:
    def __init__(self, user_selections):
        self.user_selections = user_selections

    def get_model(self):
        try:
            api_key = self.user_selections["llm_api_key"]
            if api_key == "" or os.environ.get("GOOGLE_API_KEY") == "":
                st.error("Please enter your API key")
                return None
            model_name = self.user_selections["gemini_model"]
            if model_name == "":
                st.error("Please enter your model name")
                return None
            model = ChatGoogleGenerativeAI(api_key=api_key, model_name=model_name)
            # Bind the model with tools
            # tools = self.user_selections["tools"]
            # model.bind_tools(tools)
            st.success("Gemini model loaded successfully")
            return model
        except Exception as e:
            st.error(f"Error loading Gemini model: {e}")
            raise ValueError(f"Error loading Gemini model {e}")