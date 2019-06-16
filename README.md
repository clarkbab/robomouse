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

## Architecture

### Controller

The controller is responsible for tracking mouse state (position and heading) and passing resultant sensor readings to
the mouse. It then validates the mouse's response and updates the mouse's state accordingly.

The controller has two distinct operating modes: with display and without. The structure of these modes is quite
different as when using the display, we must use an event-driven model to run the steps. This is because the Turtle
library expects to be handed control after initialisation, and will respond only to registered listeners. Thus, in
display mode, we enqueue a callback to run each new step after the previous step has completed.

#### Specifications
- During each step, it should call `next_move` on the mouse object.
- It should validate the mouse's move.
- It should track the state of the mouse.
- It should enforce the maximum number of steps per move.
- It should update the display, if necessary.
- It should be possible to perform many sequential runs and report statistics on all runs.

### Display

The display is a useful tool for debugging mouse logic. 

#### Specifications
- Pausable with space bar.
- Coloured path tracking. Each time a path between two squares is traversed, the colour changes. `Red` = 1, `Orange` =
  2, `Yellow` = 3, `Green` = 4, `Blue` = 5, `Violet` = 6.
- Maze axes have numbered indexes to check mouse position.

### CLI Interface

There are three modes in which the CLI can run robomouse:

#### Modes
- Debugging mode. Passing the `--verbose` and `--display` flags, in conjunction with an increased `--delay` is helpful
  to debug mouse logic. The `--verbose` flag value is also passed as an argument to the mouse's `__init__` method so
  the developer can conditionally print debugging output from the mouse.
- Testing maze. Evaluate the performance of a mouse by running it through a maze many times. Do this by passing the
  `--runs` flag with an appropriate value. This provides you with basic statistics for the mouse's performance.
- TODO: Training mode! Run a mouse through many mazes, each with a unique topography. This is ideal for mice who can
  learn their own strategy for solving a maze.

## Acknowledgements

The motivation for this project was the Udacity Data Science Nanodegree. Some starter code was borrowed from this
project, namely the maze-drawing component based upon the
[Turtle](https://docs.python.org/3.3/library/turtle.html?highlight=turtle) library.

