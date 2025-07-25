import subprocess
import time
import os

def run_agent():
    result = subprocess.run(["python", "-m", "agentspeak", "agent.asl"], capture_output=True, text=True)
    print(result.stdout)
    # Detect missing plan by searching for a specific output
    if "No plan found for this context" in result.stdout:
        with open("need_plan.txt", "w") as f:
            f.write("get_action_context")
        print("Request for RL plan written to need_plan.txt")

def run_rl_and_merge():
    subprocess.Popen(["python", "rl_plan_generator.py"])
    time.sleep(3)  # Wait for RL to generate new_plan.asl
    subprocess.run(["python", "merge_plan.py"])

if __name__ == "__main__":
    run_agent()
    if os.path.exists("need_plan.txt"):
        run_rl_and_merge()
        print("Re-run the agent to use the new RL-generated plan.")
