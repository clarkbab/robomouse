import pdb
import numpy as np
from rotation import Rotation

class BlindMouse():
    def __init__(self, maze_dim, init_state, verbose):
        pass
    
    def next_move(self, sensors):
        """Selects the move randomly from all options.

        Arguments:
            sensors -- a tuple of left, front and right sensor readings. Won't be needing those.
        Returns:
            rot -- the next rotation in degrees.
            move -- an integer for the next move.
        """
        # A certain percentage of the time we should try to reset.
        p = 0.05
        reset = np.random.choice([0, 1], p=[(1 - p), p])
        if reset:
            return 'RESET', 'RESET'
        
        # Get random rotation. Assign a lower prob to reset.
        rot = np.random.choice(Rotation)

        # Get random move.
        move_opts = range(-3, 4)
        move = np.random.choice(move_opts)

        return rot, move

