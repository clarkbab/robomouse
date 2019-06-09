## Contents

### Mice

- [Blind Mouse](#blind-mouse)
- [Danger Mouse](#danger-mouse)
- [Reversing Danger Mouse](#reversing-danger-mouse)
- [Dead End Mouse](#dead-end-mouse)
- [Magnetic Mouse](#magnetic-mouse)
- [Tremaux Mouse](#tremaux-mouse)

### Performance Summary

[Results](#results)

## Mice

### Blind Mouse

Blind as a bat, doesn't make use of sensor readings. Makes random forward moves in any direction, regardless of whether there is a wall in the way or not. Has a 5% chance of calling `RESET` on every move.

### Danger Mouse

Can sense danger, e.g. walls. Looks at the sensor readings to calculate the set of possible forward moves and randomly selects
one. Like the Blind Mouse it has a 5% chance of calling 'RESET' on every move.

### Reversing Danger Mouse

Similar to Danger Mouse in every regard except that when this mouse finds itself in trouble (i.e. a dead end), it
reverses instead of turning around.

### Dead End Mouse

Keeps track of dead ends and avoids them in future moves. Includes the [State Mixin](mixins/README.md#state-mixin) to track its position and remember dead end locations.

### Magnetic Mouse

Favours moves towards the centre of the maze. Uses the [State Mixin](mixins/README.md#state-mixin) to track position and
heading and measure direction of centre. Moves with larger vector components in the direction of centre will be favoured.

### Tremaux Mouse

An implementation of depth-first search, this mouse will search down a branch until a leaf is reached and then
backtrack. For this method to work, the mouse must know how many times it has taken a certain path. A path is defined as
the passage between two nodes, where a node is an intersection (has an l-shape bend) or a dead-end.

As the mouse progresses through the maze it builds up a graph of the nodes it has visited. When re-tracing a passage it
can use this knowledge to move to the next node as quickly as possible.

## Results

The following results are for n=1000 trial runs.

| Mouse                   | Maze  | % Completed   | Mean Score  | Standard Dev.   |
| ----------------------- | ----- | ------------: | ----------: | --------------: |
| Blind Mouse             | 1     | 1.2           | 749.24      | 173.00          |
| "                       | 2     | 1.2           | 749.24      | 173.00          |
| "                       | 3     | 1.2           | 749.24      | 173.00          |
| Danger Mouse            | 1     | 48.1          | 459.71      | 266.10          |
| "                       | 2     | 48.1          | 459.71      | 266.10          |
| "                       | 3     | 48.1          | 459.71      | 266.10          |
| Reversing Danger Mouse  | 1     | 54.5          | 446.90      | 172.97          | 
| "                       | 2     | 54.5          | 446.90      | 172.97          | 
| "                       | 3     | 54.5          | 446.90      | 172.97          | 
| Dead End Mouse          | 1     | 46.0          | 444.45      | 259.96          |
| "                       | 2     | 46.0          | 444.45      | 259.96          |
| "                       | 3     | 46.0          | 444.45      | 259.96          |
| Magnetic Mouse          | 1     | 72.4          | 395.80      | 264.84          |
| "                       | 2     | 78.9          | 408.22      | 231.51          |
| "                       | 3     | 85.9          | 177.53      | 111.95          |
| Tremaux Mouse           | 1     | 100.0         | 141.36      | 63.87           |
| "                       | 2     | 100.0         | 189.83      | 98.24           |
| "                       | 3     | 100.0         | 198.49      | 131.59          | 
| Perfect Mouse*          | 1     | -             | 18.60       | -               |
| "                       | 2     | -             | 24.80       | -               |
| "                       | 3     | -             | 26.87       | -               |

* Perfect mouse is omniscient. This mouse makes the largest possible moves towards the goal with no planning required. No mouse should be able to beat this score on average.
