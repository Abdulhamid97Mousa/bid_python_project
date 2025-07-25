# # rl_plan_sender.py
# C:\Users\Hamid\Desktop\Transformer\bid_python_project\rl_plan_sender.py

import zmq
import time
import json
from mutations_pb2 import PlanMutation

# Example Q-table: context -> action (converted from rl_plan_generator.py)
Q_table = {
    "get_action_context": "action_rl1",
    "other_context": "action_rl2"
}

class RLPlanSender:
    def __init__(self, port=5555):
        self.context = zmq.Context()
        self.socket = self.context.socket(zmq.PUB)
        self.socket.bind(f"tcp://*:{port}")  # Fixed port, no auto-increment
        self.port = port
        print(f"RL Plan Sender started on port {port}")
        
        # Brief pause to allow socket binding to complete
        time.sleep(0.1)
        
    def publish_plan(self, context_key, action):
        """Create and publish a PlanMutation message"""
        plan_text = (
            f'+!get_action : context(C) & C == "{context_key}" <-\n'
            f'    .print("RL chosen: {action}");\n'
            f'    -context(C).'
        )
        
        mutation = PlanMutation(
            op=PlanMutation.ADD,
            prio=1,
            plan=plan_text
        )
        
        # Send with prefix framing to avoid decode confusion
        message_data = mutation.SerializeToString()
        prefixed_message = b"P" + message_data  # "P" for PlanMutation
        self.socket.send(prefixed_message)
        print(f"Published plan for context: {context_key}, action: {action}")
    
    def run_continuous(self, interval=2):
        """Run the sender continuously, similar to old file-polling behavior"""
        print("Starting continuous RL plan generation...")
        
        while True:
            try:
                # Simulate RL decision making (replace with actual RL logic)
                for context, action in Q_table.items():
                    self.publish_plan(context, action)
                    time.sleep(interval)
                    
            except KeyboardInterrupt:
                print("Stopping RL Plan Sender...")
                break
            except Exception as e:
                print(f"Error in RL Plan Sender: {e}")
                time.sleep(1)
    
    def close(self):
        """Clean shutdown"""
        self.socket.close()
        self.context.term()

if __name__ == "__main__":
    sender = RLPlanSender()
    try:
        sender.run_continuous()
    finally:
        sender.close()
