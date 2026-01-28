import streamlit as st
from src.ui.layout import Layout
from src.workflow.llms.groq_with_tools import Groq_with_tools
from src.workflow.llms.openai_with_tools import OpenAI_with_tools
from src.workflow.llms.gemini_with_tools import Gemini_with_tools
from src.workflow.graphs.chatbot_with_tools_graph import Chatbot_with_tools_graph
from src.ui.display_results import DisplayResults

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

    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat history from session state
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ask a question ...")
    
    if user_input:
        # display the user message
        with st.chat_message("user"):
            st.write(user_input)

        try:
            # Get the model from user selection
            if user_selections["llm_model"] == "Groq":
                llm_object = Groq_with_tools(user_selections=user_selections)
                # Re-initialize model if configuration changed
                model_key = f"{user_selections.get('groq_model', '')}_{user_selections.get('llm_api_key', '')}"
            
            if user_selections["llm_model"] == "OpenAI":
                llm_object = OpenAI_with_tools(user_selections=user_selections)
                # Re-initialize model if configuration changed
                model_key = f"{user_selections.get('openai_model', '')}_{user_selections.get('llm_api_key', '')}"
            
            if user_selections["llm_model"] == "Gemini":
                llm_object = Gemini_with_tools(user_selections=user_selections)
                # Re-initialize model if configuration changed
                model_key = f"{user_selections.get('gemini_model', '')}_{user_selections.get('llm_api_key', '')}"

            if "current_model_key" not in st.session_state or st.session_state.current_model_key != model_key:
                st.session_state.llm_model = llm_object.get_model()
                st.session_state.current_model_key = model_key
            
            if not st.session_state.llm_model:
                return

            # Get the use case from user selection
            use_case = user_selections["use_case"]
            if not use_case:
                st.error("Error: Use case is not selected")
                return

            # Get the graph based on the use case
            if use_case == "Chatbot with tools":
                graph_builder = Chatbot_with_tools_graph(model=st.session_state.llm_model)
                try:
                    chatbot_graph = graph_builder.build_graph()

                    # Prepare messages for the graph including history
                    chat_history = []
                    for m in st.session_state.messages:
                        if m["role"] == "user":
                            chat_history.append(HumanMessage(content=m["content"]))
                        else:
                            chat_history.append(AIMessage(content=m["content"]))
                    
                    # Add current user input
                    chat_history.append(HumanMessage(content=user_input))

                    # Display the results
                    display_results = DisplayResults(use_case=use_case, workflow=chatbot_graph, user_input=user_input)
                    display_results.display(chat_history)
                    
                    # Update session state with the new message
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    st.session_state.messages.append({"role": "assistant", "content": display_results.display(chat_history)})
                    # Rerun the app to display the new message
                    st.rerun()
                    
                except Exception as e:
                        st.error(f"Error: Failed to build basic chatbot graph {e}")
                        return
        except Exception as e:
            st.error(f"Error: {e}")
            return 

                

                
        

    
