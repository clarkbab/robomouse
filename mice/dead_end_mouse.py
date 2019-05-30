import random
import pdb
import numpy as np
from .awareness_mixin import AwarenessMixin

class DeadEndMouse(AwarenessMixin):
    MAX_MOVE = 3

    # Map from reading index to rotation.
    INDEX_ROTATION_MAP = {
        0: -90,
        1: 0,
        2: 90
    }

    def __init__(self, maze_dim, init_state, max_steps, verbose):
        super().init(maze_dim, init_state, max_steps, verbose)
        self.dead_ends = np.zeros((maze_dim, maze_dim))
        pass

    def random_move_vec(self, sensor_id, reading):
        """Selects a random move from all moves in a direction.
        """
        max_move = min([reading, self.MAX_MOVE])
        move_heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[sensor_id])

        # Some moves may lead to dead-ends.
        poss_move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for move in range(1, max_move + 1):
            move_vec = move * self.HEADING_COMPONENTS_MAP[move_heading]
            new_pos = self.pos + move_vec 

            # Only consider the move if it doesn't lead to a dead end.
            try:
                if self.dead_ends[tuple(new_pos)] == 0:
                    poss_move_vecs = np.vstack((poss_move_vecs, move_vec))
            except IndexError:
                pdb.set_trace()
        
        if len(poss_move_vecs) == 0:
            return None
        else:
            idx = np.random.choice(len(poss_move_vecs))
            return poss_move_vecs[idx]

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
            self.dead_ends[tuple(self.pos)] = 1
            self.update_state([0, 0], -90)
            return -90, 0
        
        # Choose a rotation randomly from those directions. 
        idx = random.choice(non_zero_idx)
        rot = self.INDEX_ROTATION_MAP[idx]
        
        # Choose a random move in the forward direction.
        max_move = min([sensors[idx], self.MAX_MOVE])
        move = random.choice(range(1, max_move + 1))

        return rot, move

