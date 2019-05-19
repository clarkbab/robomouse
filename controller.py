import time
import pdb
import numpy as np

class Controller:
    MAX_DEGREES = 360
    VALID_HEADINGS = [0, 90, 180, 270]
    VALID_ROTATIONS = [0, 90, -90]
    MAX_MOVE = 3 

    def __init__(self, mouse, maze, display=None, n_steps=10, delay=1000,
        paused=False):
        """Creates a controller.

        Arguments:
            mouse -- the Mouse who will navigate the maze.
            maze -- the Maze to navigate.
            display -- a method of displaying the progress.
            n_step -- the number of iterations in the game.
            delay -- the delay between iterations.
        """
        self.mouse = mouse
        self.maze = maze

        self.n_steps = n_steps
        self.delay = delay
        self.step = 0
        self.paused = paused
        self.display = display

    def run(self, init_state):
        # Validate the initial state.
        if not self.valid_state(*init_state.values()):
            return

        # Set the state.
        self.mouse_state = init_state

        # Draw the mouse.
        self.display.place_mouse(*init_state.values())

        # Register the pause handler.
        self.display.screen.onkey(self.toggle_pause, 'space')

        # Hand control over to the GUI.
        self.display.listen(self.run_step, self.delay)

    def run_step(self):
        # Has the mouse reached the centre of the maze?
        reached_goal = False

        if not self.paused:
            # Increment the step number.
            self.step += 1

            print(f"Pos: {self.mouse_state['pos']}")
            print(f"Heading: {self.mouse_state['heading']}")
            
            # Get sensor readings from maze for mouse's current position and
            # heading.
            readings = self.sensor_readings(*self.mouse_state.values())

            print(f"Readings: {readings}")

            # Update mouse's heading and position.
            rot, move = self.mouse.next_move(readings)
            
            print(f"Rot: {rot}. Move: {move}")
            
            # Return if mouse is finished planning.
            if (rot, move) == ('RESET', 'RESET'):
                if reached_goal:
                    print("Mouse finished planning.")
                    self.enqueue_step()
                    return
                else:
                    print("Mouse hasn't reached goal, can't reset.")
                    self.enqueue_step()
                    return

            # Validate the mouse's response.
            if not self.valid_rotation(rot) or not self.valid_move(move):
                self.enqueue_step()
                return

            # Update the mouse's heading and the display.
            self.mouse_state['heading'] = self.rotate_heading(self.mouse_state['heading'], rot)
            self.display.set_heading(self.mouse_state['heading']) 

            # Is the move valid given the structure of the maze?
            if not self.maze.valid_move(*self.mouse_state.values(), move):
                self.enqueue_step()
                return
            
            # Maps from heading to axis and direction.
            heading_map = {
                self.maze.NORTH: np.array([0, 1]),
                self.maze.EAST: np.array([1, 0]),
                self.maze.SOUTH: np.array([0, -1]),
                self.maze.WEST: np.array([-1, 0])
            }

            # Update the mouse's position and the display.
            self.mouse_state['pos'] += move * heading_map[self.mouse_state['heading']]
            print(self.mouse_state['pos'])
            self.display.move(self.mouse_state['pos'])
        else:
            print('paused')

        # Countdown to another iteration.
        self.enqueue_step()

    def rotate_heading(self, heading, degrees):
        """Returns the new heading.
        """
        new_heading = heading + degrees

        # Account for values outside of the accepted range.
        if new_heading >= 360:
            new_heading -= 360
        elif new_heading < 0:
            new_heading += 360

        return new_heading

    def sensor_readings(self, pos, heading):
        """Returns a tuple of sensor readings.

        Arguments:
            pos -- the mouse's current position.
            heading -- the mouse's heading.
        """
        # Get left and right headings.
        l_head = self.rotate_heading(heading, -90)
        r_head = self.rotate_heading(heading, 90)

        # Get distances to nearest wall in straight line.
        dist = self.maze.dist_to_wall(pos, heading)
        l_dist = self.maze.dist_to_wall(pos, l_head) 
        r_dist = self.maze.dist_to_wall(pos, r_head) 

        return (l_dist, dist, r_dist)

    def enqueue_step(self):
        self.display.sleep(self.run_step, self.delay)

    def toggle_pause(self):
        print('toggling!')
        self.paused = not self.paused

    def valid_state(self, pos, heading):
        """Checks if the mouse state is valid.

        Arguments:
            state -- a dict containing the keys:
                pos -- a list containing the [x, y] co-ordinates of the mouse.
                heading -- a number in degrees, must be a value from
                    VALID_HEADINGS.
        """
        # Check the position exists in the maze.
        if not self.maze.pos_exists(pos):
            return False

        # Check the heading is valid.
        if not heading in self.VALID_HEADINGS:
            print(f"Heading {heading} isn't valid, choose from {self.VALID_HEADINGS}")
            return False

        return True

    def valid_rotation(self, rot):
        """Checks if the rotation from the mouse is valid.

        Arguments:
            rot -- the rotation in degrees.
        """
        # Is this a valid rotation?
        if not rot in self.VALID_ROTATIONS:
            print(f"Invalid rotation {rot}, should be one of {self.VALID_ROTATIONS}") 
            return False 

        return True

    def valid_move(self, move):
        """Checks if the move from the mouse is valid.

        Arguments:
            move -- the move in steps.
        """
        # Is the move valid?
        if not (isinstance(move, int) and (move in range(-self.MAX_MOVE, self.MAX_MOVE +
            1))):
            print(f"Invalid move: {move}")
            return False
            
        return True

