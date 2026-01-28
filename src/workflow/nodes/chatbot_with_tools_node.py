from src.workflow.states.chatbot_with_tools_state import Chatbot_with_tools_state

class Chatbot_with_tools_node:
    def __init__(self, model):
        self.model = model

    def process(self, state: Chatbot_with_tools_state):
        
        """
        This function processes the state of the chatbot with tools.
        """
        return {"messages": self.model.invoke(state['messages'])}