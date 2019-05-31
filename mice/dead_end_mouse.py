import random
import pdb
import numpy as np
from mice.mixins import StateMixin

class DeadEndMouse(StateMixin):
    MAX_MOVE = 3

    def __init__(self, maze_dim, init_state, verbose):
        super().init(maze_dim, init_state, verbose)
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
        # Reset if the mouse has reached the goal.
        if self.in_goal():
            self.start_execution()
            return 'RESET', 'RESET'

        # Get a prob for each direction.
        sensor_ids = []
        move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for i, reading in enumerate(sensors):
            if reading == 0: continue

            # Randomly select a move in sensor's direction.
            move_vec = self.random_move_vec(i, reading) 
            
            # Maybe we can't move in this direction because it's a dead end.
            if move_vec is None: continue
            move_vecs = np.vstack((move_vecs, move_vec))
            
            # Register this index as movable.
            sensor_ids.append(i)

        # If no possible moves, mark dead end and turn around. 
        if len(move_vecs) == 0:
            # Mark dead end on map.
            self.dead_ends[tuple(self.pos)] = 1
            self.update_state(-90, [0, 0])
            return -90, 0
        
        # Get an index based on the probs.
        sensor_id = np.random.choice(sensor_ids)
        
        # Get the rotation and move to perform.
        rot = self.SENSOR_ROTATION_MAP[sensor_id]
        move_vec = move_vecs[sensor_ids.index(sensor_id)]
        move = abs(move_vec).max()

        print(f"[MOUSE] Pos: {self.pos}")
        print(f"[MOUSE] Heading: {self.heading}")

        # Update internal state.
        self.update_state(rot, move_vec)
        
        return rot, move

