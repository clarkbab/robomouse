import random
import numpy as np

class MemoryMouse:
    MAX_MOVE = 3

    # Map from reading index to rotation.
    INDEX_ROTATION_MAP = {
        0: -90,
        1: 0,
        2: 90
    }

    def __init__(self, maze_dim):
        self.pos = np.array([0, 0])
        self.heading = 0
        self.memory = np.zeros(maze_dim, maze_dim)
        self.memory[0, 0] = 1
        pass

    def next_move(self, sensors, reached_goal):
        if reached_goal:
            return 'RESET', 'RESET'

        # Get indexes where readings are non-zero.
        non_zero_idx = np.where(np.array(sensors) > 0)[0]

        # If all sensors are blank, turn around. This requires two moves.
        if len(non_zero_idx) == 0:
            self.dead_end = True
            return -90, 0
           
        # Choose a rotation randomly from those directions. 
        idx = random.choice(non_zero_idx)
        rot = self.INDEX_ROTATION_MAP[idx]
        
        # Choose a random move in the forward direction.
        max_move = min([sensors[idx], self.MAX_MOVE])
        move = random.choice(range(1, max_move + 1))

        # Update new pos.




