import streamlit as st
from src.ui.layout import Layout
from src.workflow.llms.groq import Groq
from src.workflow.llms.openai import OpenAI
from src.workflow.llms.gemini import Gemini
from src.workflow.graphs.chatbot_graph import Chatbot_graph
from src.workflow.graphs.chatbot_with_tools_graph import Chatbot_with_tools_graph
from src.workflow.graphs.ai_news_summarizer_graph import AINewsSummarizerGraph
from src.ui.display_results import DisplayResults
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage
from src.ui.graph_display import GraphDisplay

def load_layout():
    """
    This function loads the layout of the application. 
    User selections are stored in the session state.
    User selections are validated.
    """
    layout = Layout()
    user_selections = layout.render()
    
    if not user_selections:
        st.error("Error: User selections are not valid")
        return

    # Get the use case from user selection
    use_case = user_selections["use_case"]
    if not use_case:
        st.error("Error: Use case is not selected")
        return

    # Initialize chat history for each use case
    history_key = f"messages_{use_case}"
    if history_key not in st.session_state:
        st.session_state[history_key] = []

    # Display logic
    if use_case == "AI News Summarizer":
        # Display "Latest" for AI News Summarizer if it exists at the top
        latest_news = None
        if st.session_state[history_key]:
            for msg in reversed(st.session_state[history_key]):
                if msg["role"] == "assistant":
                    latest_news = msg["content"]
                    break
                    
        if latest_news:
            st.subheader(f"Latest {use_case} Result")
            with st.chat_message("assistant"):
                st.markdown(latest_news)
                st.download_button(
                    label="📥 Download Markdown",
                    data=latest_news,
                    file_name="ai_news_summary.md",
                    mime="text/markdown",
                    key="download_md"
                )
            st.divider()

        # Display remaining history for AI News Summarizer (reversed so latest FETCH is at top)
        st.subheader("Previous Summaries")
        curr_latest = latest_news # local copy for history loop
        for message in reversed(st.session_state[history_key]):
            # Skip the latest news if we already displayed it at top
            if curr_latest and message["role"] == "assistant" and message["content"] == curr_latest:
                curr_latest = None 
                continue
            
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    else:
        # Standard Chatbot display (Chronological: Top to Bottom)
        for message in st.session_state[history_key]:
            if message["role"] == "tool":
                with st.expander("🔧 View Tool Execution Details"):
                    st.markdown(f"**Tool Output:**\n{message['content']}")
            else:
                # Don't display empty assistant messages (bubbles for tool calls)
                if message["role"] == "assistant" and not message["content"]:
                    continue
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

    # Determine user input source
    user_input = None
    if use_case == "AI News Summarizer":
        if st.session_state.get("IS_AI_NEWS_FETCHED", False):
            user_input = st.session_state.time_frame
            # Reset the flag so it doesn't trigger again on next rerun
            st.session_state.IS_AI_NEWS_FETCHED = False 
    else:
        user_input = st.chat_input("Ask a question ...")
    
    if user_input:
        # display the user message (only if not from the internal fetch button, 
        # or maybe we want to show 'Fetching Daily News' as a message)
        with st.chat_message("user"):
            st.write(user_input if use_case != "AI News Summarizer" else f"Fetching {user_input} Latest AI News")

        try:
            # Get the model from user selection
            if user_selections["llm_model"] == "Groq":
                llm_object = Groq(user_selections=user_selections)
                model_key = f"{user_selections.get('groq_model', '')}_{user_selections.get('llm_api_key', '')}"
            
            elif user_selections["llm_model"] == "OpenAI":
                llm_object = OpenAI(user_selections=user_selections)
                model_key = f"{user_selections.get('openai_model', '')}_{user_selections.get('llm_api_key', '')}"
            
            elif user_selections["llm_model"] == "Gemini":
                llm_object = Gemini(user_selections=user_selections)
                model_key = f"{user_selections.get('gemini_model', '')}_{user_selections.get('llm_api_key', '')}"

            if "current_model_key" not in st.session_state or st.session_state.current_model_key != model_key:
                st.session_state.llm_model = llm_object.get_model()
                st.session_state.current_model_key = model_key
            
            if not st.session_state.llm_model:
                return

            # Create a unique key for the current configuration (model + use case)
            config_key = f"{model_key}_{use_case}"
            
            # Check if we need to rebuild the graph
            if "chatbot_graph" not in st.session_state or st.session_state.get("current_config_key") != config_key:
                try:
                    # Get the graph based on the user selected use case
                    if use_case == "Chatbot":
                        graph_builder = Chatbot_graph(model=st.session_state.llm_model)
                        st.session_state.chatbot_graph = graph_builder.build_graph()
                        GraphDisplay().display_graph(st.session_state.chatbot_graph)
                    
                    elif use_case == "Chatbot with Web Search":
                        graph_builder = Chatbot_with_tools_graph(model=st.session_state.llm_model)
                        st.session_state.chatbot_graph = graph_builder.build_graph()
                        GraphDisplay().display_graph(st.session_state.chatbot_graph)

                    elif use_case == "AI News Summarizer":
                        graph_builder = AINewsSummarizerGraph(model=st.session_state.llm_model)
                        st.session_state.chatbot_graph = graph_builder.build_graph()
                        GraphDisplay().display_graph(st.session_state.chatbot_graph)
                    
                    st.session_state.current_config_key = config_key
                except Exception as e:
                    st.error(f"Error: Failed to build chatbot graph: {e}")
                    return

            chatbot_graph = st.session_state.chatbot_graph

            try:
                # Prepare messages for the graph including history
                chat_history = []
                for m in st.session_state[history_key]:
                    if m["role"] == "user":
                        chat_history.append(HumanMessage(content=m["content"]))
                    elif m["role"] == "tool":
                        chat_history.append(ToolMessage(content=m["content"], tool_call_id="unknown"))
                    else:
                        chat_history.append(AIMessage(content=m["content"]))
                
                # Add current user input
                chat_history.append(HumanMessage(content=user_input))

                # Display the results
                display_results = DisplayResults(use_case=use_case, workflow=chatbot_graph, user_input=user_input)
                
                # Update session state with the new messages
                st.session_state[history_key].append({"role": "user", "content": user_input if use_case != "AI News Summarizer" else f"Fetching {user_input} Latest AI News"})
                st.session_state[history_key].extend(display_results.display(chat_history))
                # Rerun the app to display the new messages
                st.rerun()
                
            except Exception as e:
                    st.error(f"Error executing graph: {e}")
                    return
        except Exception as e:
            st.error(f"Error: {e}")
            return 

                

                
        

    
