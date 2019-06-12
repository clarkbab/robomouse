from heading import Heading

class State:
    def __init__(self, pos, heading):
        # Store the initial state.
        self.init_pos = pos
        self.init_heading = heading

        # Reset the state.
        self.reset()

    def update(self, rot, move):
        self.heading = Heading.rotate(self.heading, rot)
        self.pos += move * Heading.components(self.heading)

    def reset(self):
        self.pos = self.init_pos
        self.heading = self.init_heading

