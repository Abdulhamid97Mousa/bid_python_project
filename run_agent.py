# run_agent.py
# C:\Users\Hamid\Desktop\Transformer\bid_python_project\run_agent.py
import dql_module

class Agent:
    def __init__(self, state):
        self.state = state
        print("Agent started.")

    def get_action(self):
        action = dql_module.get_action(self.state)
        print("Action chosen by DQL:", action)
        return action

if __name__ == "__main__":
    agent = Agent("default_state")
    agent.get_action()
