import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

class DisplayResults:
    def __init__(self,use_case,workflow,user_input):
        self.use_case = use_case
        self.workflow = workflow
        self.user_input = user_input

    def display(self, messages):
        use_case = self.use_case
        workflow = self.workflow
        generated_messages = []
        
        if use_case == "Chatbot":
            full_response = ""
            # Stream the response from the workflow
            for event in workflow.stream({"messages": messages}):
                for value in event.values():
                    if 'messages' in value:
                        response_msg = value['messages']
                        if isinstance(response_msg, list):
                            response_msg = response_msg[-1]
                        
                        # Use a context manager for the assistant message
                        if isinstance(response_msg, AIMessage):
                            with st.chat_message("assistant"):
                                message_placeholder = st.empty()
                                full_response += response_msg.content
                                message_placeholder.markdown(full_response)
                                generated_messages.append({"role": "assistant", "content": response_msg.content})
            
            return generated_messages

        elif use_case == "Chatbot with Web Search":
            # Stream the response from the workflow
            for event in workflow.stream({"messages": messages}):
                for value in event.values():
                    if 'messages' in value:
                        msg_data = value['messages']
                        if isinstance(msg_data, list):
                            msg_to_process = msg_data[-1]
                        else:
                            msg_to_process = msg_data
                        
                        # Use expander for tool outputs
                        if isinstance(msg_to_process, ToolMessage):
                            with st.expander("🔧 View Tool Execution Details"):
                                st.markdown(f"**Tool Output:**\n{msg_to_process.content}")
                            generated_messages.append({"role": "tool", "content": msg_to_process.content})

                        # Use a context manager for the assistant message
                        if isinstance(msg_to_process, AIMessage):
                            # Record the message in history regardless of content if it has tool calls
                            # Or if it has content, display and record it.
                            if msg_to_process.content:
                                with st.chat_message("assistant"):
                                    message_placeholder = st.empty()
                                    message_placeholder.markdown(msg_to_process.content)
                                generated_messages.append({"role": "assistant", "content": msg_to_process.content})
                            elif msg_to_process.tool_calls:
                                # We add it to history but don't necessarily need a UI bubble for an empty tool call
                                generated_messages.append({"role": "assistant", "content": ""}) 
                        
            return generated_messages

        elif use_case == "AI News Summarizer":
            frequency = self.user_input
            with st.spinner(f"Fetching and summarising the news for {frequency}..."):
                # The workflow invoke returns the final state
                response_state = workflow.invoke({"messages": messages})
                summary = response_state.get("summary", "")
                
                if summary:
                    # Capture the summary but don't display it here if we want it at the top in main.py
                    # Actually, if I display it here, it will be at the bottom of where main calls it.
                    # I'll return it so main.py can choose.
                    generated_messages.append({"role": "assistant", "content": summary})
                    return generated_messages
                else:
                    st.error("Error: Failed to generate AI news summary.")
                    return []
                
                
        