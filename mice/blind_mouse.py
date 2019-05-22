import random

class BlindMouse():
    def __init__(self, maze_dim):
    
    def next_move(self, sensors):
        """Selects the move randomly from all options.

        Arguments:
            sensors -- a tuple of left, front and right sensor readings. Won't be needing those.
        """
        # Get random rotation.
        rot_opts = [-90, 0, 90, 'RESET']
        rot = random.choice(rot_opts)

        if rot == 'RESET':
            return rot, rot     # We said it was blind, not stupid.

        # Get random move.
        move_opts = range(-3, 4)
        move = random.choice(move_opts)

        return rot, move

