import random

class BlindMouse():
    def __init__(self, maze_dim, init_state, verbose=False):
        self.reached_goal = False
        pass

    def signal_reached_goal(self):
        self.reached_goal = True

    def signal_end_run(self):
        self.reached_goal = False
    
    def next_move(self, sensors):
        """Selects the move randomly from all options.

        Arguments:
            sensors -- a tuple of left, front and right sensor readings. Won't be needing those.
        Returns:
            rot -- the next rotation in degrees.
            move -- an integer for the next move.
        """
        if self.reached_goal:
            self.reached_goal = False
            return 'RESET', 'RESET'     # We said it was blind, not stupid.

        # Get random rotation.
        rot_opts = [-90, 0, 90]
        rot = random.choice(rot_opts)

        # Get random move.
        move_opts = range(-3, 4)
        move = random.choice(move_opts)

        return rot, move

