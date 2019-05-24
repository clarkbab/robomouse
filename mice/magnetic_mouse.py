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
        
    def normalize(self, value):
        """Squashes the centre component to the range 0.3 to 1.
        """
        return (1 - 0.3) * (value + self.MAX_MOVE) / (2 * self.MAX_MOVE) + 0.3

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

        # If all sensors are blank, turn around. This requires two moves.
        if len(non_zero_idx) == 0:
            self.dead_end = True
            return -90, 0
            
        move_vecs = np.zeros((len(sensors), 2), np.int8)
        weights = np.zeros(len(sensors))
        for i, reading in enumerate(sensors):
            # Give a zero weight if we can't move in that direction.
            if reading == 0:
                continue

            # Randomly select a move in that direction.
            max_move = min([reading, self.MAX_MOVE])
            move = random.choice(range(1, max_move + 1))

            # Get the move vector.
            move_heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[i])
            move_vec = move * self.HEADING_COMPONENTS_MAP[move_heading]
            move_vecs[i] = move_vec

            # How much of this move is towards the centre?
            centre_comp = np.dot(move_vec, self.unit_centre())

            # Normalise this component to the range (0.3, 1). Why not (0, 1)? We still want -3
            # moves to have a chance!
            weight = self.normalize(centre_comp)
            weights[i] = weight

        # Smooth so values sum to one.
        probs = weights / sum(weights)
        
        # Get an index based on the probs.
        idx = np.random.choice(3, p=probs)
        
        # Get the rotation and move to perform.
        rot = self.SENSOR_ROTATION_MAP[idx]
        move = abs(move_vecs[idx]).max()
        
        # Update internal state.
        self.pos += move_vecs[idx]
        self.heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[idx])

        return rot, move
