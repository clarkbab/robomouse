# RoboMouse

A 2D learning environment based upon [Micromouse](https://en.wikipedia.org/wiki/Micromouse).

## Problem Statement

### Overview

In the maze game, a mouse must obtain the lowest possible score based upon two phases in the maze. These phases are the
planning and execution phases. 

During the planning phase, the mouse moves around the maze, eventually finding the centre and then signalling a `RESET` at
its leisure. The idea is the mouse takes this time to plan the best route to use during the execution phase, when brevity
yields a lower overall score.

The execution phase is similar to the planning phase except once the mouse reaches the centre, the run is finished.

### Game Specifics

The final score is calculated using the formula: E = m<sub>P</sub>S<sub>P</sub> + S<sub>E</sub>, where m<sub>P</sub> is the
multiplier for the planning phase (1/30), S<sub>P</sub> is the number of steps taken planning and S<sub>E</sub> is the number of steps taken for execution. 

During each step of the game, the mouse is presented with a reading from each of its left, front and right-facing
sensors. Using this information, it must return a rotation and move to make that turn. Possible rotations are -90, 0
and 90 degrees. Possible moves are single squares in the range -3 to 3 inclusive.

The mouse is provided with the dimension of the maze. The goal is always the centre 2x2 box of the maze, so the mouse
can determine when it has reached the goal.

Each phase iterates for a maximum number of steps (default 1000). If the mouse reaches this number of steps for either
phase, it has failed the run and will get no score. If you want an example of this, run the blind mouse..

Impossible moves, such as walking through walls or moving diagonally won't be performed but will count towards step
count.

## Getting Started

### Running

Example mice reside in the [mice](mice) folder. To test a mouse run the following:

```bash
$ ./micromouse --mouse MagneticMouse --maze mazes/maze_01.txt --verbose --display --delay 500
```

For a full list of CLI options, run:

```bash
$ ./micromouse --help
```

### Scoring

To test a mouse over many runs, you can use the command:

```bash
$ ./micromouse --mouse MagneticMouse --mazes/maze_01.txt --runs 1000
```

At the end of the runs, the following metrics will be shown:

- Percentage of successful runs.
- Average score for all successful runs.
- Standard deviation of the score for all successful runs.

### Building a Mouse

Follow info [here](mice/README.md#building-a-mouse). 

