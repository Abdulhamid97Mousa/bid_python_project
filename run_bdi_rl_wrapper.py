import subprocess
import time
import os

def run_agent_and_monitor():
    # Run the agent and capture output
    result = subprocess.run(["python", "-m", "agentspeak", "agent.asl"], capture_output=True, text=True)
    print(result.stdout)
    # If RL is needed, trigger RL workflow
    if "No plan found for this context. Requesting RL..." in result.stdout:
        with open("need_plan.txt", "w") as f:
            f.write("get_action_context")
        print("RL request written to need_plan.txt")
        # Run RL generator
        subprocess.run(["python", "rl_plan_generator.py"])
        # Merge RL-generated plan
        subprocess.run(["python", "merge_plan.py"])
        print("RL plan merged. Re-running agent...")
        # Re-run agent to use new plan
        result2 = subprocess.run(["python", "-m", "agentspeak", "agent.asl"], capture_output=True, text=True)
        print(result2.stdout)

if __name__ == "__main__":
    run_agent_and_monitor()
