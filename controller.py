import time
import pdb
import numpy as np
import copy

class Controller:
    HEADING_RANGE = (0, 360)
    VALID_HEADINGS = (0, 90, 180, 270)
    VALID_ROTATIONS = (0, 90, -90)
    MAX_STEPS = 3 
    PLAN_RUN = 0
    EXEC_RUN = 1

    def __init__(self, mouse, maze, display=None, steps=10, delay=1000, pause=False, verbose=True):
        """Creates a controller.

        Arguments:
            mouse -- the Mouse who will navigate the maze.
            maze -- the Maze to navigate.
            display -- a method of displaying the progress.
            steps -- the number of iterations in the game.
            delay -- the delay between iterations.
            pause -- should we pause before runs.
            verbose -- prints info to the command line.
        """
        self.mouse = mouse
        self.maze = maze
        self.steps = steps
        self.delay = delay
        self.step = np.zeros(2)
        self.pause = pause
        if self.pause:
            self.paused = True
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
        self.run = self.PLAN_RUN
        self.init_state = init_state
        self.mouse_state = copy.deepcopy(init_state)
        self.reached_goal = False

        # Draw the mouse.
        self.display.place_mouse(*self.mouse_state.values())

        # Register the pause handler.
        if self.pause:
            self.display.screen.onkey(self.toggle_pause, 'space')

        # Hand control over to the GUI.
        self.display.listen(self.run_step, self.delay)

    def start_execution(self):
        # Clear the current mouse tracks.
        self.display.clear_track()
        
        # Put into execution mode.
        self.run = self.EXEC_RUN

        # Reset the mouse state and position.
        self.mouse_state = copy.deepcopy(self.init_state)
        self.display.place_mouse(*self.mouse_state.values())

        # Set up state.
        self.reached_goal = False
        if self.pause:
            self.paused = True

        # Begin steps.
        self.enqueue_step()

    def run_step(self):
        """Runs one iteration of the maze problem.

        This method re-enqueues itself when the mouse is finished performing its turn.
        """
        # Increment the step count if not paused.
        if not (self.pause and self.paused):
            self.step[self.run] += 1
        else:
            if self.verbose: print('paused')
            self.enqueue_step()
            return

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
        if self.run == self.PLAN_RUN and (rot, move) == ('RESET', 'RESET'):
            if self.reached_goal:
                if self.verbose: print("Mouse finished planning.")
                
                # Start execution run.
                self.start_execution()

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

        # Check if mouse has reached goal.
        if (not self.reached_goal) and self.maze.reached_goal(self.mouse_state['pos']):
            if self.verbose: print(f"Mouse reached goal {self.mouse_state['pos']}.")
            self.reached_goal = True

            # Check if mouse has completed the final run.
            if self.run == self.EXEC_RUN:
                self.display.close()
                return

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
        print('-----')
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

    def score(self):
        """Calculates the mouse's score for the run.
        """
        # Return nothing if the mouse hasn't finished the maze.
        if not (self.run == self.EXEC_RUN and self.reached_goal):
            print("Mouse not finished.")
            return

        # Steps in the planning round aren't penalised as highly.
        plan_mult = 1 / 30

        # Calculate the score.
        score = self.step[self.EXEC_RUN] + plan_mult * self.step[self.PLAN_RUN] 

        return score

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

