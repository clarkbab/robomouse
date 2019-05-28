import numpy as np

class AwarenessMixin:
    PLAN_RUN = 0
    EXEC_RUN = 1
    
    def init(self, maze_dim, init_state):
        self.init_state = init_state
        self.maze_dim = maze_dim
        self.run = self.PLAN_RUN
        self.max_steps = 1000
        self.reset_state()

    def reset_state(self):
        self.step = 0
        self.reached_goal = False
        self.pos = np.array(self.init_state['pos'], dtype=np.int8)
        self.heading = self.init_state['heading'] 

    def in_goal(self):
        """Checks if we're in the centre of the maze.
        """
        # Both axes will have the same goal co-ordinates.
        goal_coords = [self.maze_dim / 2 - 1, self.maze_dim / 2]

        # Check if position in goal.
        if not (self.pos[0] in goal_coords and self.pos[1] in goal_coords):
            return False

        return True

    def 

