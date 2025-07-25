!start.
state(default_state).
energy(100).

+!start <-
    .print("Agent started.");
    !get_action.

+!get_action : state(other_state) & energy(E) & E > 20 <-
    .print("Action chosen: action2");
    -state(other_state);
    +state(final_state);
    -energy(E);
    +energy(E-20);
    !get_action.

+!get_action : state(final_state) <-
    .print("Agent finished. No more actions.").

+!get_action : energy(E) & E <= 20 <-
    .print("Not enough energy to continue.").

+!get_action <-
    .print("RL chosen: action_rl1").
    // Add more actions here
