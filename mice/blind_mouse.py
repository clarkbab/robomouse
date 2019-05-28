import random

class BlindMouse():
    def __init__(self, maze_dim, init_state):
        pass
    
    def next_move(self, sensors, reached_goal):
        """Selects the move randomly from all options.

        Arguments:
            sensors -- a tuple of left, front and right sensor readings. Won't be needing those.
            reached_goal -- a boolean indicating True if the goal has been reached.
        Returns:
            rot -- the next rotation in degrees.
            move -- an integer for the next move.
        """
        if reached_goal:
            return 'RESET', 'RESET'     # We said it was blind, not stupid.

        # Get random rotation.
        rot_opts = [-90, 0, 90]
        rot = random.choice(rot_opts)

        # Get random move.
        move_opts = range(-3, 4)
        move = random.choice(move_opts)

        return rot, move

