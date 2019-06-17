import random
import pdb
import numpy as np
from rotation import Rotation
from sensor import Sensor

class DangerMouse:
    MAX_MOVE = 3

    def __init__(self, maze_dim, init_state, verbose):
        pass

    def next_move(self, sensors):
        """Selects the move randomly, but avoids walls. He's sick of banging his head.

        Arguments:
            sensors -- a tuple of left, front and right sensor readings.
            reached_goal -- a boolean indicating True if the goal has been reached.
        Returns:
            rot -- the next rotation in degrees.
            move -- an integer for the next move.
        """
        # A certain percentage of the time we should try to reset.
        p = 0.05
        reset = np.random.choice([0, 1], p=[(1 - p), p])
        if reset:
            return 'RESET', 'RESET'

        # Get indexes where readings are non-zero.
        non_zero_idx = np.where(np.array(sensors) > 0)[0]

        # If all sensors are blank, turn around.
        if len(non_zero_idx) == 0:
            return Rotation.LEFT, 0
        
        # Choose a rotation randomly from those directions. 
        idx = random.choice(non_zero_idx)
        rot = Sensor(idx).rotation()
        
        # Choose a random move in the forward direction.
        max_move = min([sensors[idx], self.MAX_MOVE])
        move = random.choice(range(1, max_move + 1))

        return rot, move

