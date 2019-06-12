import random
import pdb
import numpy as np
from mice.mixins import StateMixin
from heading import Heading
from rotation import Rotation
from sensor import Sensor

class DeadEndMouse(StateMixin):
    MAX_MOVE = 3

    def __init__(self, maze_dim, init_state, verbose):
        super().init(maze_dim, init_state, verbose)
        self.dead_ends = np.zeros((maze_dim, maze_dim))
        pass

    def random_move_vec(self, sensor, reading):
        """Selects a random move from all moves in a direction.
        """
        max_move = min([reading, self.MAX_MOVE])
        rot = Sensor.rotation(sensor)
        move_heading = Heading.rotate(self.heading, rot) 

        # Some moves may lead to dead-ends.
        poss_move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for move in range(1, max_move + 1):
            move_vec = move * Heading.components(move_heading)
            new_pos = self.pos + move_vec 

            # Only consider the move if it doesn't lead to a dead end.
            if self.dead_ends[tuple(new_pos)] == 0:
                poss_move_vecs = np.vstack((poss_move_vecs, move_vec))
        
        if len(poss_move_vecs) == 0:
            return None
        else:
            idx = np.random.choice(len(poss_move_vecs))
            return poss_move_vecs[idx]

    def next_move(self, readings):
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
        sensors = np.array([])
        move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for i, reading in enumerate(readings):
            if reading == 0: continue

            # Create the sensor.
            sensor = Sensor(i)

            # Randomly select a move in sensor's direction.
            move_vec = self.random_move_vec(sensor, reading) 
            
            # Maybe we can't move in this direction because it's a dead end.
            if move_vec is None: continue
            move_vecs = np.vstack((move_vecs, move_vec))
            
            # Register this index as movable.
            sensors = np.append(sensors, sensor)

        # If no possible moves, mark dead end and turn around. 
        if len(move_vecs) == 0:
            # Mark dead end on map.
            self.dead_ends[tuple(self.pos)] = 1
            self.update_state(Rotation.LEFT, 0)
            return Rotation.LEFT, 0
        
        # Get an index based on the probs.
        sensor = np.random.choice(sensors)
        
        # Get the rotation and move to perform.
        rot = Sensor.rotation(sensor)
        idx = np.where(sensors == sensor)[0][0]
        move_vec = move_vecs[idx]
        move = abs(move_vec).max()

        # Update internal state.
        self.update_state(rot, move) 
        
        return rot, move

