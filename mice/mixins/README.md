## Contents

- [State Mixin](#state-mixin)

## Mixins

### State Mixin

Provides a collection of functions for tracking the state of the mouse.

- `init`, sets the initial state of the mouse, e.g. position and heading.
- `reset_state`, sets the mouse's state back to initial, used between planning and execution runs. 
- `update_state`, sets the mouse's new state after each move.
- `start_execution`, sets mode to `execution`, is `planning` initially. 
- `new_heading`, takes a rotation value and calculates the mouse's new heading.
- `in_goal`, checks if the mouse is in the goal.

