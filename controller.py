import time
import pdb
import numpy as np
import copy

class Controller:
    HEADING_RANGE = (0, 360)
    VALID_HEADINGS = (0, 90, 180, 270)
    VALID_ROTATIONS = (0, 90, -90)
    MAX_STEPS_PER_MOVE = 3 
    PLAN_RUN = 0
    EXEC_RUN = 1

    def __init__(self, mouse, maze, init_state, max_steps=10, delay=1000, pause=False, verbose=True):
        """Creates a maze game controller.

        Arguments:
            mouse -- the Mouse who will navigate the maze.
            maze -- the Maze to navigate.
            init_state -- the mouse's starting state.
            max_steps -- the number of iterations in the game.
            delay -- the delay in ms between iterations.
            pause -- should we pause before runs.
            verbose -- prints info to the command line.
        """
        # Validate the initial state.
        self.validate_state(*init_state.values(), maze)

        self.mouse = mouse
        self.maze = maze
        self.init_state = init_state
        self.max_steps = max_steps
        self.steps = np.zeros(2)
        self.delay = delay
        self.pause = pause
        self.verbose = verbose

    def run_with_display(self, display):
        """Runs the maze game in display mode.

        Arguments:
            display -- the Display to write to.
        Returns:
            True, if the mouse successfully completed the game, False otherwise.
        """
        # Enter planning mode.
        self.planning_mode()

        # Set up the display.
        self.display = display
        self.display.draw_maze()
        self.display.place_mouse(*self.mouse_state.values())

        # Set up space bar pause.
        self.display.on_space(self.toggle_pause)

        # Start the planning phase.
        self.display.screen.ontimer(self.run_display_step, self.delay)

        # Sets the screen to focus, to allow for key events.
        self.display.screen.listen()

        # Start the main loop, this must be the last line of the GUI
        # application. Can be broken later with 'turtle.bye()'.
        self.display.mainloop()

        # If the mouse wasn't successful, return False.
        if not (self.run == self.EXEC_RUN and self.reached_goal):
            return False

        return True

    def planning_mode(self):
        """Sets up the controller state in preparation for a planning run.
        """
        # Pause if requested.
        self.paused = True if self.pause else False
        
        # Set the run type.
        self.run = self.PLAN_RUN

        # Reset the step counter.
        self.steps[self.PLAN_RUN] = 0
        
        # Reset the mouse's state.
        self.mouse_state = copy.deepcopy(self.init_state)

        # Reset the success flags.
        self.reached_goal = False
        self.planning_complete = False

    def run_display_step(self):
        """Handles the running of a step when in display mode.

        Calls 'turtle.bye()' when mouse has finished, either successfully or otherwise.
        """
        # Skip step if paused.
        if self.paused:
            if self.verbose: print('paused')
            self.display.sleep(self.run_display_step, self.delay)
            return

        # Run the step.
        finished = self.run_step()

        # Update the display.
        self.display.set_heading(self.mouse_state['heading'])
        self.display.move(self.mouse_state['pos'])
       
        # Check if finished.
        if not finished:
            # Enqueue another step if not finished.
            self.display.sleep(self.run_display_step, self.delay)
            return 
        elif self.run == self.PLAN_RUN and self.planning_complete:
            # If finished planning run, start the execution run.
            self.execution_mode()

            # Reset display.
            self.display.clear_track()
            self.display.place_mouse(*self.mouse_state.values())
            
            # Start the next run.
            self.display.sleep(self.run_display_step, self.delay)
            return

        # Mouse has finished, exit Turtle main loop.
        self.display.close()

    def execution_mode(self):
        """Sets up the controller state in preparation for an execution run.
        """
        # Pause if requested.
        self.paused = True if self.pause else False

        # Set run type.
        self.run = self.EXEC_RUN

        # Reset the step counter.
        self.steps[self.EXEC_RUN] = 0

        # Reset the mouse state and position.
        self.mouse_state = copy.deepcopy(self.init_state)

        # Reset success flag.
        self.reached_goal = False

    def run(self):
        """Runs the maze game in normal mode.

        Returns:
            True if mouse successfuly completed game, False otherwise.
        """
        # Set to planning mode.
        self.planning_mode()

        # Run for the max number of iterations.
        while self.steps[self.run] < self.max_steps:
            # Skip step if paused.
            if self.paused:
                input('Paused. Press Enter to continue...')
                self.toggle_pause()
                continue

            # Run a step.
            finished = self.run_step()

            # Check if finished.
            if finished:
                # If finished planning, start execution run.
                if self.run == self.PLAN_RUN and self.planning_complete:
                    self.execution_mode()
                elif self.run == self.EXEC_RUN and self.reached_goal:
                    # If finished execution, signal success.
                    return True

            # Sleep for specified delay.
            time.sleep(self.delay / 1000)

        # We must have gone over the max steps, signal failure.
        return False

    def run_step(self):
        """Runs one iteration of the maze problem.

        Returns:
            True if mouse finished run, else False.
        """
        self.steps[self.run] += 1

        # Get sensor readings.
        readings = self.maze.sensor_readings(*self.mouse_state.values())

        # Get mouse's desired move.
        rot, move = self.mouse.next_move(readings)
        
        if self.verbose:
            print('-----')
            print(f"Pos: {self.mouse_state['pos']}")
            print(f"Heading: {self.mouse_state['heading']}")
            print(f"Sensors: {readings}")
            print(f"Rot: {rot}")
            print(f"Move: {move}")
        
        # Check if mouse has finished planning.
        if self.run == self.PLAN_RUN and (rot, move) == ('RESET', 'RESET'):
            if self.reached_goal:
                self.planning_complete = True
                if self.verbose: print("Mouse finished planning.")
                return True
            else:
                if self.verbose: print("Mouse hasn't reached goal, can't reset.")
                return False

        # Validate the mouse's response.
        if not self.valid_rotation(rot) or not self.valid_move(move):
            return False

        # Update the mouse's heading.
        self.mouse_state['heading'] = self.maze.new_heading(self.mouse_state['heading'], rot)

        # Is the move valid given the structure of the maze?
        if not self.maze.valid_move(*self.mouse_state.values(), move):
            if self.verbose:
                print(f"Moving {move} squares in heading {self.mouse_state['heading']} from {self.mouse_state['pos']} is invalid.")
            return False

        # Update the mouse's position.
        self.mouse_state['pos'] = self.maze.new_pos(*self.mouse_state.values(), move)

        # Check if mouse has reached goal.
        if (not self.reached_goal) and self.maze.reached_goal(self.mouse_state['pos']):
            if self.verbose: print(f"Mouse reached goal {self.mouse_state['pos']}.")
            self.reached_goal = True

            # Check if mouse has completed the final run.
            if self.run == self.EXEC_RUN:
                self.execution_complete = True
                return True

        # Mouse hasn't finished, keep going.
        return False

    def toggle_pause(self):
        """Toggles the paused state.
        """
        self.paused = not self.paused

    def score(self):
        """Calculates the mouse's score for the run.
        """
        # Return nothing if the mouse hasn't finished the maze.
        if not (self.run == self.EXEC_RUN and self.reached_goal):
            if self.verbose: print("Mouse not finished.")
            return None

        # Steps in the planning round aren't penalised as highly.
        plan_mult = 1 / 30

        # Calculate the score.
        score = self.steps[self.EXEC_RUN] + plan_mult * self.steps[self.PLAN_RUN] 

        return score

    def validate_state(self, pos, heading, maze):
        """Checks if the mouse's state is valid.

        Arguments:
            pos -- a list containing the [x, y] co-ordinates of the mouse.
            heading -- a number in degrees, must be a value from VALID_HEADINGS.
            maze -- the maze to validate against.
        """
        # Check the position exists in the maze.
        if not maze.pos_exists(pos):
            raise Exception(f"Pos {pos} doesn't exist in maze.")

        # Check the heading is valid.
        if not heading in self.VALID_HEADINGS:
            raise Exception(f"Heading {heading} isn't valid, choose from {self.VALID_HEADINGS}.")

    def valid_rotation(self, rot):
        """Checks if the rotation from the mouse is valid.

        Arguments:
            rot -- the rotation in degrees.
        Returns:
            True if valid, False otherwise.
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
        Returns:
            True if valid, False otherwise.
        """
        # Is the move valid?
        if not (isinstance(move, int) and (move in range(-self.MAX_STEPS_PER_MOVE, self.MAX_STEPS_PER_MOVE + 1))):
            print(f"Invalid move: {move}")
            return False
            
        return True

