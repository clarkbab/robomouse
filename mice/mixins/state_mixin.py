import numpy as np

class StateMixin:
    PLAN_RUN = 0
    EXEC_RUN = 1
    HEADING_RANGE = range(360)
    
    # Map from reading index to rotation.
    SENSOR_ROTATION_MAP = {
        0: -90,
        1: 0,
        2: 90
    }

    # Maps a heading to its vector components.
    HEADING_COMPONENTS_MAP = {
        0: np.array([0, 1], dtype=np.int8),
        90: np.array([1, 0], dtype=np.int8),
        180: np.array([0, -1], dtype=np.int8),
        270: np.array([-1, 0], dtype=np.int8)
    }
    
    def init(self, maze_dim, init_state, verbose):
        """Initialises the mouse for a planning run.
        """
        self.init_state = init_state
        self.maze_dim = maze_dim
        self.verbose = verbose
        self.run = self.PLAN_RUN
        self.reset_state()

    def reset_state(self):
        self.reached_goal = False
        self.heading = self.init_state['heading'] 
        self.pos = np.array(self.init_state['pos'], dtype=np.int8)

    def update_state(self, rot, move):
        self.heading = self.new_heading(self.heading, rot)
        self.pos += move * self.HEADING_COMPONENTS_MAP[self.heading]

    def start_execution(self):
        self.run = self.EXEC_RUN
        self.reset_state()

    def new_heading(self, heading, rot):
        """Calculates the new heading.

        Arguments:
            heading -- the heading in degrees.
            rot -- the rotation in degrees.
        Returns:
            the new heading wrapped to the range (0, 360].
        """
        new_heading = heading + rot

        # Account for values outside of the accepted range.
        if new_heading >= len(self.HEADING_RANGE):
            new_heading -= len(self.HEADING_RANGE)
        elif new_heading < min(self.HEADING_RANGE):
            new_heading += len(self.HEADING_RANGE)

        return new_heading

    def in_goal(self):
        """Checks if we're in the centre of the maze.
        """
        # Both axes will have the same goal co-ordinates.
        goal_coords = [self.maze_dim / 2 - 1, self.maze_dim / 2]

        # Check if position in goal.
        if not (self.pos[0] in goal_coords and self.pos[1] in goal_coords):
            return False

        return True

