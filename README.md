# RoboMouse

A 2D learning environment based upon [Micromouse](https://en.wikipedia.org/wiki/Micromouse).

## Problem Statement

In the maze game, a mouse must obtain the lowest possible score based upon two runs in the maze. These runs are the
planning and execution runs. 

During the planning run, the mouse moves around the maze, eventually finding the centre and then signalling a RESET at
its leisure. The idea is the mouse takes this time to plan the best route to use during the execution run, when brevity
yields a lower overall score.

The execution run is similar to the planning run except once the mouse reaches the centre, the round is finished. The
final score is calculated using the formula: E = m * S_P + S_E, where m is the multiplier for the planning round (1 /
30), S_P is the number of steps taken planning and S_E is the number of steps taken for execution. 

### Game Specifics

During each step of the game, the mouse is presented with a reading from each of its left, front and right-facing
sensors. Using this information, it determines a rotation and move to make in that order. Possible rotations are -90, 0
and 90 degrees. Possible moves are single squares in the range -3 to 3.

The mouse is given the dimension of the maze and as the goal is always in the centre, it knows the location of the goal.

Each run, iterates for a maximum number of steps (default 1000). If the mouse is still navigating after this many steps, it
has failed the run and will get no score. If you want an example of this, run the blind mouse..

Impossible moves, such as walking through walls or moving diagonally won't be performed but will count towards step
count.

## Getting Started

### Building a Mouse

Implementing a mouse is easy! Just create a new mouse class in the /mice folder and implement the `next_move` method.
You may find visual feedback handy when debugging, get this by passing the `--display` flag.

### Testing

Learnt models reside in the [/mice](/mice) folder. You can get the score for the mouse by running the following:

```bash
$ ./run --maze mazes/maze_01.txt --mouse mice/blind_mouse.py
```

## Acknowledgements

Micromouse...
Udacity...

