import numpy as np
from heading import Heading

class State:
    def __init__(self, pos, heading):
        # Store the initial state.
        self.init_pos = np.array(pos, dtype=np.int8)
        self.init_heading = heading

        # Reset the state.
        self.reset()

    def update(self, rot, move):
        self.heading = self.heading.rotate(rot)
        self.pos += move * self.heading.components()

    def reset(self):
        self.pos = self.init_pos.copy()
        self.heading = self.init_heading

