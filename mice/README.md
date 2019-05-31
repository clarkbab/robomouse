## Contents

### Mice

- [Blind Mouse](#blind-mouse)
- [Danger Mouse](#danger-mouse)
- [Reversing Danger Mouse](#reversing-danger-mouse)
- [Dead End Mouse](#dead-end-mouse)
- [Magnetic Mouse](#magnetic-mouse)

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

## Results

The following results are for n=1000 trial runs.

| Mouse                   | Maze  | % Completed   | Mean Score  | Standard Dev.   |
| ----------------------- | ----- | ------------: | ----------: | --------------: |
| Blind Mouse             | 1     | 1.2           | 749.24      | 173.00          |
| Danger Mouse            | 1     | 48.1          | 459.71      | 266.10          |
| Reversing Danger Mouse  | 1     | 54.5          | 446.90      | 172.97          | 
| Dead End Mouse          | 1     | 46.0          | 444.45      | 259.96          |
| Magnetic Mouse          | 1     | 72.4          | 395.80      | 264.84          |

