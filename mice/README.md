## Building a Mouse

Implementing a mouse is easy! Just create a new mouse class in this folder and implement the `__init__` and `next_move`
methods.

### `__init__(self, maze_dim, init_state, verbose)`

  - maze_dim, an integer, the dimension of the maze. E.g. 12 for a 12x12 maze.
  - init_state, a dict with 'pos' and 'heading' keys. Pos is a numpy array with [x,y] coordinates of the starting
    position in the maze. Heading is a Heading enum object with one of the three possible headings. 
  - verbose, a boolean flag indicating whether the CLI runner has requested verbosity. Useful for debugging mouse logic.

### `next_move(self, readings)`

  - readings, a tuple of sensors readings from the (left, forward, right) sensors. 

## Example Mice

The following are some examples of mice, progressing in sophistication.

### `Blind Mouse`

Blind as a bat, doesn't make use of sensor readings. Makes random forward moves in any direction, regardless of whether there is a wall in the way or not. Has a 5% chance of calling `RESET` on every move.

### `Danger Mouse`

Can sense danger, e.g. walls. Looks at the sensor readings to calculate the set of possible forward moves and randomly selects
one. Like the Blind Mouse it has a 5% chance of calling `RESET` on every move.

### `Reversing Danger Mouse`

Similar to Danger Mouse in every regard except that when this mouse finds itself in trouble (i.e. a dead end), it
reverses instead of turning around.

### `Dead End Mouse`

Keeps track of dead ends and avoids them in future moves. A dead end includes squares with one exit, and those passages leading to such squares. Includes the state to track its position and remember dead end locations.

### `Magnetic Mouse`

Uses state to calculate the direction of the goal at each step and favours moves towards centre. Also remembers and
avoids dead ends.

To favour moves towards the centre, the move vector is projected onto a unit vector pointing from the mouse to the maze
centre. This produces a scalar in the range from -3 to 3 inclusive for each possible move. We use the [softmax
function](https://en.wikipedia.org/wiki/Softmax_function) to calculate the probability of performing each possible move.

### `Trémaux Mouse`

An early implementation of [depth-first search](https://en.wikipedia.org/wiki/Depth-first_search), this mouse will search
down a branch until a leaf is reached and then backtrack. For this method to work, the mouse must know how many times it 
has taken a certain path. A path is defined as the passage between two nodes, where a node is an intersection (has an
l-shape bend) or a dead-end.

As the mouse progresses through the maze it builds up a graph of the nodes it has visited. When re-tracing a passage it
can use this knowledge to move to the next node as quickly as possible.

### `A* Mouse`

Uses the Trémaux algorithm to explore the maze, noting the nodes passed on the way. Once the planning run is finished,
the mouse finds the shortest path from start to finish using the [`A* search algorithm`](https://en.wikipedia.org/wiki/A*_search_algorithm). It then completes the maze using this path.

## Results

The following results are for n=1000 trial runs.

| Mouse                   | Maze  | % Completed   | Mean Score  | Standard Dev.   |
| ----------------------- | ----- | ------------: | ----------: | --------------: |
| Blind Mouse             | 1     | 1.2           | 749.24      | 173.00          |
|                         | 2     | 1.2           | 749.24      | 173.00          |
|                         | 3     | 1.2           | 749.24      | 173.00          |
| Danger Mouse            | 1     | 48.1          | 459.71      | 266.10          |
|                         | 2     | 48.1          | 459.71      | 266.10          |
|                         | 3     | 48.1          | 459.71      | 266.10          |
| Reversing Danger Mouse  | 1     | 54.5          | 446.90      | 172.97          | 
|                         | 2     | 54.5          | 446.90      | 172.97          | 
|                         | 3     | 54.5          | 446.90      | 172.97          | 
| Dead End Mouse          | 1     | 46.0          | 444.45      | 259.96          |
|                         | 2     | 46.0          | 444.45      | 259.96          |
|                         | 3     | 46.0          | 444.45      | 259.96          |
| Magnetic Mouse          | 1     | 72.4          | 395.80      | 264.84          |
|                         | 2     | 78.9          | 408.22      | 231.51          |
|                         | 3     | 85.9          | 177.53      | 111.95          |
| Trémaux Mouse           | 1     | 100.0         | 141.36      | 63.87           |
|                         | 2     | 100.0         | 189.83      | 98.24           |
|                         | 3     | 100.0         | 198.49      | 131.59          | 
| A-Star Mouse            | 1     | 100.0         | 29.61       | 4.36            |
|                         | 2     | 100.0         | 41.10       | 4.18            | 
|                         | 3     | 100.0         | 43.91       | 5.01            | 
| `Perfect Mouse*`        | 1     | -             | 18.60       | -               |
|                         | 2     | -             | 24.80       | -               |
|                         | 3     | -             | 26.87       | -               |

* Perfect mouse is omniscient. This mouse makes the largest possible moves towards the goal with no planning required. No mouse can beat this score.
