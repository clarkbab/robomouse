import random
import pdb
import numpy as np

class MagneticMouse: # MagneticMouse?
    MAX_MOVE = 3
    HEADING_RANGE = range(360)

    # Map from reading index to rotation.
    SENSOR_ROTATION_MAP = {
        0: -90,
        1: 0,
        2: 90
    }

    # Maps a heading to its axial components.
    HEADING_COMPONENTS_MAP = {
        0: np.array([0, 1], dtype=np.int8),
        90: np.array([1, 0], dtype=np.int8),
        180: np.array([0, -1], dtype=np.int8),
        270: np.array([-1, 0], dtype=np.int8)
    }

    def __init__(self, maze_dim):
        self.pos = np.array([0, 0], dtype=np.int8)
        self.heading = 0
        self.centre = np.array([(maze_dim - 1) / 2, (maze_dim - 1) / 2])

    def unit_centre(self):
        """Finds the unit vector from the mouse to the centre.
        """
        vec = self.centre - self.pos
        unit_vec = vec / np.linalg.norm(vec)
        return unit_vec
        
    def softmax(self, values):
        """Performs the softmax function on the list of input values.
        """
        # Shift the values so the maximum is zero.
        values -= np.max(values)

        return np.exp(values) / np.sum(np.exp(values))

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
        
    def next_move(self, sensors, reached_goal):
        if reached_goal:
            return 'RESET', 'RESET'

        # Get indexes where readings are non-zero.
        non_zero_idx = np.where(np.array(sensors) > 0)[0]

        # If all sensors are blank, turn around.
        if len(non_zero_idx) == 0:
            self.heading = self.new_heading(self.heading, -90)
            return -90, 0
            
        # Get a prob for each direction.
        sensor_ids = []
        weights = []
        move_vecs = []
        for i, reading in enumerate(sensors):
            if reading == 0:
                continue
                
            # Register this index as movable.
            sensor_ids.append(i)

            # Randomly select a move in that direction.
            max_move = min([reading, self.MAX_MOVE])
            move = random.choice(range(1, max_move + 1))

            # Get the move vector.
            move_heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[i])
            move_vec = move * self.HEADING_COMPONENTS_MAP[move_heading]
            move_vecs.append(move_vec)

            # How much of this move is towards the centre?
            weight = np.dot(move_vec, self.unit_centre())
            weights.append(weight)

        # Apply the softmax function.
        probs = self.softmax(weights)
        
        # Get an index based on the probs.
        sensor_id = np.random.choice(sensor_ids, p=probs)
        
        # Get the rotation and move to perform.
        rot = self.SENSOR_ROTATION_MAP[sensor_id]
        move_vec = move_vecs[sensor_ids.index(sensor_id)]
        move = abs(move_vec).max()
        
        # Update internal state.
        self.pos += move_vec
        self.heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[sensor_id])

        return rot, move
