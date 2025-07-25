def merge_new_plan():
    try:
        with open("new_plan.asl") as newf, open("agent.asl", "a") as agentf:
            agentf.write("\n" + newf.read())
        print("Merged new RL plan into agent.asl")
    except FileNotFoundError:
        print("No new plan to merge.")

if __name__ == "__main__":
    merge_new_plan()
