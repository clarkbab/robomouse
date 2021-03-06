import time
import pdb
import numpy as np
import copy
from heading import Heading
from rotation import Rotation
from state import State
from phase import Phase

class Controller:
    MAX_STEPS = 3 

    def __init__(self, mouse, maze, init_state, max_steps=10, delay=1000, pause=False, verbose=True):
        """Creates a maze game controller.

        Arguments:
            mouse -- the Mouse who will navigate the maze.
            maze -- the Maze to navigate.
            init_state -- the mouse's starting state.
            max_steps -- the maximum number of steps per phase.
            delay -- the delay in ms between steps.
            pause -- should we pause before runs.
            verbose -- prints info to the command line.
        """
        # Create mouse's state.
        self.mouse_state = State(init_state['pos'], init_state['heading'])

        # Validate the initial state.
        self.validate_state(self.mouse_state.pos, self.mouse_state.heading, maze)

        # Keep record of mouse object. This prevents the mouse from persisting state between runs.
        self.initial_mouse = mouse

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
        self.display.place_mouse(self.mouse_state.pos, self.mouse_state.heading)

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
        if not (self.phase == Phase.EXECUTE and self.reached_goal):
            return False

        return True

    def planning_mode(self):
        """Sets up the controller state in preparation for a planning run.
        """
        # Create a new copy of mouse.
        self.mouse = copy.deepcopy(self.initial_mouse)

        # Pause if requested.
        self.paused = True if self.pause else False
        
        # Set the run type.
        self.phase = Phase.PLAN

        # Reset the step counter.
        self.steps[Phase.PLAN.value] = -1
        
        # Reset the mouse's state.
        self.mouse_state.reset()

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

        # Keep old mouse pos to see if we moved at all.
        old_pos = self.mouse_state.pos.copy()

        # Run the step.
        finished = self.run_step()

        # If we've taken too long, exit.
        if self.steps[self.phase.value] >= (self.max_steps - 1):
            self.display.close()
            return

        # Update the display.
        self.display.set_heading(self.mouse_state.heading)
        if not np.array_equal(self.mouse_state.pos, old_pos):
            self.display.move(self.mouse_state.pos)
       
        # Check if finished.
        if not finished:
            # Enqueue another step if not finished.
            self.display.sleep(self.run_display_step, self.delay)
            return 
        elif self.phase == Phase.PLAN and self.planning_complete:
            # If finished planning run, start the execution run.
            self.execution_mode()

            # Reset display.
            self.display.clear_track()
            self.display.place_mouse(self.mouse_state.pos, self.mouse_state.heading)
            
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
        self.phase = Phase.EXECUTE

        # Reset the step counter.
        self.steps[Phase.EXECUTE.value] = -1

        # Reset the mouse state and position.
        self.mouse_state.reset()

        # Reset success flag.
        self.reached_goal = False

    def run_normal(self):
        """Runs the maze game in normal mode.

        Returns:
            True if mouse successfuly completed game, False otherwise.
        """
        # Set to planning mode.
        self.planning_mode()

        # Run for the max number of steps.
        while self.steps[self.phase.value] < (self.max_steps - 1):
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
                if self.phase == Phase.PLAN and self.planning_complete:
                    self.execution_mode()
                elif self.phase == Phase.EXECUTE and self.reached_goal:
                    # If finished execution, signal success.
                    return True

            # Sleep for specified delay.
            time.sleep(self.delay / 1000)

        return False

    def run_step(self):
        """Runs one step of the maze problem.

        Returns:
            True if mouse finished run, else False.
        """
        self.steps[self.phase.value] += 1

        # Get sensor readings.
        readings = self.maze.sensor_readings(self.mouse_state.pos, self.mouse_state.heading)

        if self.verbose:
            print('-----')
            print(f"Phase: {self.phase.value}")
            print(f"Step: {self.steps[self.phase.value]:.0f}")
            print(f"Pos: {self.mouse_state.pos}")
            print(f"Heading: {self.mouse_state.heading.value}")
            print(f"Sensors: {readings}")

        # Get mouse's desired move.
        rot, move = self.mouse.next_move(readings)
        
        # Check if mouse has finished planning.
        if self.phase == Phase.PLAN and (rot, move) == ('RESET', 'RESET'):
            if self.reached_goal:
                self.planning_complete = True
                if self.verbose: print("Finished planning.")
                return True
            else:
                if self.verbose: print("Mouse hasn't reached goal, can't reset.")
                return False

        if self.verbose:
            print(f"Rot: {rot.value}")
            print(f"Move: {move}")

        # Validate the mouse's response.
        if not self.valid_rotation(rot) or not self.valid_move(move):
            return False

        # Is the move valid given the structure of the maze?
        new_heading = self.mouse_state.heading.rotate(rot)
        if not self.maze.valid_move(self.mouse_state.pos, new_heading, move):
            if self.verbose:
                print(f"Moving {move} squares in heading {new_heading.value} from {self.mouse_state.pos} is invalid.")
            return False

        # Update the mouse's state.
        self.mouse_state.update(rot, move)

        # Check if mouse has reached goal.
        if (not self.reached_goal) and self.maze.reached_goal(self.mouse_state.pos):
            if self.verbose: print(f"Reached goal {self.mouse_state.pos}.")
            self.reached_goal = True

            # Check if mouse has completed the final run.
            if self.phase == Phase.EXECUTE:
                if self.verbose: print(f"Finished.")
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
        if not (self.phase == Phase.EXECUTE and self.reached_goal):
            return None

        # Steps in the planning round aren't penalised as highly.
        plan_mult = 1 / 30

        # Calculate the score.
        score = self.steps[Phase.EXECUTE.value] + plan_mult * self.steps[Phase.PLAN.value] 

        return score

    def validate_state(self, pos, heading, maze):
        """Checks if the mouse's state is valid.

        Arguments:
            pos -- a list containing the [x, y] co-ordinates of the mouse.
            heading -- a Heading, e.g. Heading.NORTH.
            maze -- the maze to validate against.
        """
        # Check the position exists in the maze.
        if not maze.pos_exists(pos):
            raise Exception(f"Pos {pos} doesn't exist in maze.")

        # Check the heading is valid.
        if not heading in Heading:
            raise Exception(f"Heading {heading} isn't valid, must be a Heading.")

    def valid_rotation(self, rot):
        """Checks if the rotation from the mouse is valid.

        Arguments:
            rot -- a Rotation, e.g. Rotation.LEFT.
        Returns:
            True if valid, False otherwise.
        """
        # Is this a valid rotation?
        if not rot in Rotation:
            if self.verbose: print(f"Invalid rot {rot}, must be a Rotation.") 
            return False 

        return True

    def valid_move(self, move):
        """Checks if the move from the mouse is valid.

        Arguments:
            move -- the move in steps.
        Returns:
            True if valid, False otherwise.
        """
        # Is it an integer?
        if not move % 1 == 0:
            print(f"Move should be integer, got: {move}")
            return False

        # Check it's in the correct range.
        if not move in range(-self.MAX_STEPS, self.MAX_STEPS + 1):
            print(f"Move should be in range ({-self.MAX_STEPS},{self.MAX_STEPS}), got {move}.")
            return False
            
        return True

