import time
import pdb
import numpy as np

class Controller:
    HEADING_RANGE = (0, 360)
    VALID_HEADINGS = (0, 90, 180, 270)
    VALID_ROTATIONS = (0, 90, -90)
    MAX_STEPS = 3 

    def __init__(self, mouse, maze, display=None, steps=10, delay=1000, paused=False, verbose=True):
        """Creates a controller.

        Arguments:
            mouse -- the Mouse who will navigate the maze.
            maze -- the Maze to navigate.
            display -- a method of displaying the progress.
            steps -- the number of iterations in the game.
            delay -- the delay between iterations.
            paused -- the initial state of the controller.
            verbose -- prints info to the command line.
        """
        self.mouse = mouse
        self.maze = maze
        self.steps = steps
        self.delay = delay
        self.step = 0
        self.paused = paused
        self.display = display
        self.verbose = verbose

    def start(self, init_state):
        """Initiates the maze game.
        
        Hands control over to the display to begin game iterations.

        Arguments:
            init_state -- the mouse's initial state.
        """
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
        """Runs one iteration of the maze problem.

        This method re-enqueues itself when the mouse is finished performing its turn.
        """
        # Has the mouse reached the centre of the maze?
        reached_goal = False

        # If paused, enqueue a new step and finish.
        if self.paused:
            if self.verbose: print('paused')
            self.enqueue_step()
            return

        # Increment the step number.
        self.step += 1

        # Get sensor readings from maze for mouse's current position and
        # heading.
        readings = self.sensor_readings(*self.mouse_state.values())

        # Update mouse's heading and position.
        rot, move = self.mouse.next_move(readings)
        
        if self.verbose:
            print(f"Pos: {self.mouse_state['pos']}")
            print(f"Heading: {self.mouse_state['heading']}")
            print(f"Sensors: {readings}")
            print(f"Rot: {rot}")
            print(f"Move: {move}")
        
        # Return if mouse is finished planning.
        if (rot, move) == ('RESET', 'RESET'):
            if reached_goal:
                if self.verbose: print("Mouse finished planning.")
                self.enqueue_step()
                return
            else:
                if self.verbose: print("Mouse hasn't reached goal, can't reset.")
                self.enqueue_step()
                return

        # Validate the mouse's response.
        if not self.valid_rotation(rot) or not self.valid_move(move):
            self.enqueue_step()
            return

        # Update the mouse's heading.
        self.mouse_state['heading'] = self.rotate_heading(self.mouse_state['heading'], rot)

        # Write new heading to the display.
        self.display.set_heading(self.mouse_state['heading']) 

        # Is the move valid given the structure of the maze?
        if not self.maze.valid_move(*self.mouse_state.values(), move):
            self.enqueue_step()
            return

        # Update the mouse's position.
        self.mouse_state['pos'] += move * self.heading_axis_map()[self.mouse_state['heading']]

        # Write the new position to the display.
        self.display.move(self.mouse_state['pos'])

        # Enqueue another iteration.
        self.enqueue_step()

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
        """Enqueues another step.
        """
        self.display.sleep(self.run_step, self.delay)

    def toggle_pause(self):
        """Toggles the paused state.
        """
        self.paused = not self.paused

    def heading_axis_map(self):
        """Maps a unit move in a heading to axis values.
        """
        return { 
            self.maze.NORTH: np.array([0, 1]),
            self.maze.EAST: np.array([1, 0]),
            self.maze.SOUTH: np.array([0, -1]),
            self.maze.WEST: np.array([-1, 0])
        }

    def rotate_heading(self, heading, rot):
        """Returns the new heading within the range (0, 360].

        Arguments:
            heading -- the current heading.
            rot -- the rotation in degrees.
        """
        new_heading = heading + rot

        # Account for values outside of the accepted range.
        if new_heading >= self.HEADING_RANGE[1]:
            new_heading -= self.HEADING_RANGE[1]
        elif new_heading < self.HEADING_RANGE[0]:
            new_heading += self.HEADING_RANGE[1] 

        return new_heading

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
            if self.verbose: print(f"Pos {pos} doesn't exist.")
            return False

        # Check the heading is valid.
        if not heading in self.VALID_HEADINGS:
            if self.verbose: print(f"Heading {heading} isn't valid, choose from {self.VALID_HEADINGS}.")
            return False

        return True

    def valid_rotation(self, rot):
        """Checks if the rotation from the mouse is valid.

        Arguments:
            rot -- the rotation in degrees.
        """
        # Is this a valid rotation?
        if not rot in self.VALID_ROTATIONS:
            if self.verbose: print(f"Invalid rot {rot}, choose from {self.VALID_ROTATIONS}.") 
            return False 

        return True

    def valid_move(self, move):
        """Checks if the move from the mouse is valid.

        Arguments:
            move -- the move in steps.
        """
        # Is the move valid?
        if not (isinstance(move, int) and (move in range(-self.MAX_STEPS, self.MAX_STEPS + 1))):
            print(f"Invalid move: {move}")
            return False
            
        return True

