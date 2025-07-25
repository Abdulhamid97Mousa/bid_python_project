import time
import os

# Example Q-table: context -> action
Q_table = {
    "get_action_context": "action_rl1",
    "other_context": "action_rl2"
}

def generate_plan(context):
    action = Q_table.get(context, "default_action")
    plan = (
        f'+!get_action : context(C) & C == {context} <-\n'
        f'    .print("RL chosen: {action}");\n'
        f'    -context(C).\n'
        f'    // Add more actions here\n'
    )
    return plan

while True:
    if os.path.exists("need_plan.txt"):
        with open("need_plan.txt") as f:
            context = f.read().strip()
        if context:
            plan = generate_plan(context)
            with open("new_plan.asl", "w") as f:
                f.write(plan)
            open("need_plan.txt", "w").close()  # Clear request
            print(f"RL generated new plan for context: {context}")
    time.sleep(2)
