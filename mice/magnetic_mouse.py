import random
import pdb
import numpy as np
from mice.mixins import StateMixin

class MagneticMouse(StateMixin):
    MAX_MOVE = 3
    HEADING_RANGE = range(360)

    # Maps a heading to its axial components.
    HEADING_COMPONENTS_MAP = {
        0: np.array([0, 1], dtype=np.int8),
        90: np.array([1, 0], dtype=np.int8),
        180: np.array([0, -1], dtype=np.int8),
        270: np.array([-1, 0], dtype=np.int8)
    }

    def __init__(self, maze_dim, init_state, verbose):
        """Sets up the mouse's initial state.
        """
        super().init(maze_dim, init_state, verbose)
        self.maze_centre = np.array([(maze_dim - 1) / 2, (maze_dim - 1) / 2])
        self.dead_ends = np.zeros((maze_dim, maze_dim))
        self.verbose = verbose

    def unit_centre(self):
        """Finds the unit vector from the mouse to the centre.
        """
        vec = self.maze_centre - self.pos
        unit_vec = vec / np.linalg.norm(vec)
        return unit_vec
        
    def softmax(self, values):
        """Performs the softmax function on the list of input values.
        """
        # Shift the values so the maximum is zero.
        values -= np.max(values)
        return np.exp(values) / np.sum(np.exp(values))

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
        # Print mouse's assumed location.
        if self.verbose:
            print(f"[MOUSE] Run: {self.run}")
            print(f"[MOUSE] Pos: {self.pos}")
            print(f"[MOUSE] Heading: {self.heading}")

        # Update mouse's state.
        rot, move = self.make_move(sensors)

        # Check if we're in the goal.
        if self.in_goal():
            self.reached_goal = True
            if self.verbose:
                print(f"[MOUSE] Reached goal.")

            if self.run == self.EXEC_RUN:
                if self.verbose: print(f"[MOUSE] Finished.")

        return rot, move

    def make_move(self, sensors):
        # Check if we should reset.
        if self.reached_goal:
            if self.verbose: print(f"[MOUSE] Finished planning.")
            self.start_execution()
            return 'RESET', 'RESET'

        # Get a prob for each direction.
        sensor_ids = []
        weights = []
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

            # How much of this move is towards the centre?
            weight = np.dot(move_vec, self.unit_centre())
            weights.append(weight)

        # If no possible moves, mark dead end and turn around. 
        if len(move_vecs) == 0:
            # Mark dead end on map.
            self.dead_ends[tuple(self.pos)] = 1

            # Turn around.
            self.update_state(-90, [0, 0])
            return -90, 0

        # Apply the softmax function.
        probs = self.softmax(weights)
        
        # Get an index based on the probs.
        sensor_id = np.random.choice(sensor_ids, p=probs)
        
        # Get the rotation and move to perform.
        rot = self.SENSOR_ROTATION_MAP[sensor_id]
        move_vec = move_vecs[sensor_ids.index(sensor_id)]
        move = abs(move_vec).max()
        
        # Update internal state.
        self.update_state(rot, move_vec) 

        return rot, move
