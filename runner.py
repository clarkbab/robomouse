import time
import sys
import numpy as np

from maze import Maze
from mouse import Mouse
from display import Display
from controller import Controller

if __name__ == '__main__':

    # Create a maze based on input argument on command line.
    maze = Maze(str(sys.argv[1]))

    # Create the display module.
    display = Display(maze)

    # Draw the maze.
    display.draw_maze()

    # Create and place the mouse.
    mouse = Mouse(maze.dim)
    init_state = { 'pos': np.array([0, 2]), 'heading': Maze.NORTH }

    # Create manager.
    controller = Controller(mouse, maze, display, paused=True, delay=100)

    # Run planning round.
    controller.run(init_state)

    print('finished')

