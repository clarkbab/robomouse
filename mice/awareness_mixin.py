import numpy as np

class AwarenessMixin:
    PLAN_RUN = 0
    EXEC_RUN = 1
    
    def init(self, maze_dim, init_state, max_steps, verbose):
        """Initialises the mouse for a planning run.
        """
        self.init_state = init_state
        self.maze_dim = maze_dim
        self.max_steps = max_steps
        self.verbose = verbose
        self.start_planning()

    def reset_state(self):
        self.step = 0
        self.reached_goal = False
        self.pos = np.array(self.init_state['pos'], dtype=np.int8)
        self.heading = self.init_state['heading'] 

    def update_state(self, move_vec, rot):
        self.pos += move_vec
        self.heading = self.new_heading(self.heading, rot)

    def start_planning(self):
        self.run = self.PLAN_RUN
        self.reset_state()

    def start_execution(self):
        self.run = self.EXEC_RUN
        self.reset_state()

    def increment(self):
        """Increments the step count.

        Returns:
            True if over the step limit, False otherwise.
        """
        self.step += 1

        # Check if we've gone over the limit.
        return True if self.step > (self.max_steps - 1) else False

    def in_goal(self):
        """Checks if we're in the centre of the maze.
        """
        # Both axes will have the same goal co-ordinates.
        goal_coords = [self.maze_dim / 2 - 1, self.maze_dim / 2]

        # Check if position in goal.
        if not (self.pos[0] in goal_coords and self.pos[1] in goal_coords):
            return False

        return True

