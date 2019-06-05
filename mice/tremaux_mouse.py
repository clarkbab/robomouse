import pdb
import numpy as np
from mice.mixins import StateMixin

class TremauxMouse(StateMixin):
    def __init__(self, maze_dim, init_state, verbose):
        super().init(maze_dim, init_state, verbose)
        self.maze_centre = np.array([(maze_dim - 1) / 2, (maze_dim - 1) / 2])
        self.paths = np.zeros((maze_dim ** 2, maze_dim ** 2), dtype=np.int8)
        self.back_track = False
        self.last_path = 0

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
        shift_values = values - np.max(values)
        return np.exp(shift_values) / np.sum(np.exp(shift_values))

    def unique_index(self, pos):
        return pos[0] + self.maze_dim * pos[1]

    def increment_path(self, old_pos, new_pos):
        from_idx = self.unique_index(old_pos)
        to_idx = self.unique_index(new_pos)
        self.paths[from_idx, to_idx] += 1
        self.paths[to_idx, from_idx] += 1
        return self.paths[from_idx, to_idx]

    def next_move(self, sensors):
        # Print mouse's assumed location.
        if self.verbose:
            print(f"[MOUSE] run: {self.run}")
            print(f"[MOUSE] pos: {self.pos}")
            print(f"[MOUSE] heading: {self.heading}")

        # Updates mouse's state.
        rot, move = self.make_move(sensors)

        # check if we're in the goal.
        if self.in_goal():
            self.reached_goal = True
            if self.verbose:
                print(f"[MOUSE] reached goal.")

            if self.run == self.EXEC_RUN:
                if self.verbose: print(f"[MOUSE] finished.")

        return rot, move

    def make_move(self, sensors):
        # Check if we should reset.
        if self.reached_goal:
            if self.verbose: print(f"[MOUSE] Finished planning.")
            self.start_execution()
            return 'RESET', 'RESET'

        # Check if we're backtracking.
        if self.back_track:
            old_pos = self.pos.copy()
            move_heading = self.new_heading(self.heading, -90)
            move_vec = self.HEADING_COMPONENTS_MAP[move_heading]
            self.update_state(-90, move_vec) 
            self.last_path = self.increment_path(old_pos, self.pos)
            self.back_track = False
            return -90, 1

        # Get a prob for each direction.
        sensor_ids = np.array([], dtype=np.int8)
        weights = np.array([], dtype=np.float32)
        visits = np.array([], dtype=np.int8)
        move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for i, reading in enumerate(sensors):
            if reading == 0: continue

            # Get the move vector components.
            move_heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[i])
            move_vec = self.HEADING_COMPONENTS_MAP[move_heading]

            # Check if the move will take us down a visited path.
            new_pos = self.pos + move_vec
            from_idx = self.unique_index(self.pos)
            to_idx = self.unique_index(new_pos)
            visit = self.paths[from_idx, to_idx]
            if visit == 2:
                continue
            
            # Add the number of visits to this location.
            visits = np.append(visits, visit)

            # Add the move vec and sensor ID.
            move_vecs = np.vstack((move_vecs, move_vec))
            sensor_ids = np.append(sensor_ids, i)

            # How much of this move is towards the centre?
            weight = np.dot(move_vec, self.unit_centre())
            weights = np.append(weights, weight)

        # If no possible moves, mark dead end and turn around. 
        if len(move_vecs) == 0:
            # Turn around.
            self.update_state(-90, [0, 0])

            # Otherwise we'll keep turning around.
            self.last_path = 0
            return -90, 0

        # Take the road less travelled, i.e, select those squares that we've visited less.
        min_idx = np.argwhere(visits == np.min(visits)).flatten()

        # If we've visited all paths in the junction, and we've only come from this direction once, turn around
        # because we're in a loop.
        if np.min(visits) == 1 and self.last_path == 1:
            # Turn around and head back the way we came.
            self.back_track = True
            self.update_state(-90, [0, 0])
            return -90, 0

        sensor_ids = sensor_ids[min_idx]
        weights = weights[min_idx]
        move_vecs = move_vecs[min_idx]

        # Apply the softmax function.
        probs = self.softmax(weights)
        
        # Get a sensor based on the probs.
        sensor_id = np.random.choice(sensor_ids, p=probs)
        idx = np.where(sensor_ids == sensor_id)[0][0]

        # Get the rotation and move to perform.
        rot = self.SENSOR_ROTATION_MAP[sensor_id]
        move_vec = move_vecs[idx]
        move = abs(move_vec).max()
        
        # Update internal state.
        old_pos = self.pos.copy()
        self.update_state(rot, move_vec) 

        # Keep track of last path in case we need to turn around.
        self.last_path = self.increment_path(old_pos, self.pos)

        return rot, move

