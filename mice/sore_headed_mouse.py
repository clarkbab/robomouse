import random
import pdb
import numpy as np

class SoreHeadedMouse:
    MAX_MOVE = 3

    # Map from reading index to rotation.
    INDEX_ROTATION_MAP = {
        0: -90,
        1: 0,
        2: 90
    }

    def __init__(self, maze_dim):
        # Set up state.
        self.dead_end = False
        pass

    def next_move(self, sensors, reached_goal):
        """Selects the move randomly, but avoids walls. He's sick of banging his head.

        Arguments:
            sensors -- a tuple of left, front and right sensor readings.
            reached_goal -- a boolean indicating True if the goal has been reached.
        Returns:
            rot -- the next rotation in degrees.
            move -- an integer for the next move.
        """
        if reached_goal:
            return 'RESET', 'RESET'     # We said it was blind, not stupid.
        elif self.dead_end:
            self.dead_end = False
            return -90, 0

        # Get indexes where readings are non-zero.
        non_zero_idx = np.where(np.array(sensors) > 0)[0]

        # If all sensors are blank, turn around. This requires two moves.
        if len(non_zero_idx) == 0:
            self.dead_end = True
            return -90, 0
        
        # Choose a rotation randomly from those directions. 
        idx = random.choice(non_zero_idx)
        rot = self.INDEX_ROTATION_MAP[idx]
        
        # Choose a random move in the forward direction.
        max_move = min([sensors[idx], self.MAX_MOVE])
        move = random.choice(range(1, max_move + 1))

        return rot, move

