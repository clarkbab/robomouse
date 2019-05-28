import numpy as np

class MouseMixin:
    def reset_state(self):
        self.reached_goal = False
        self.pos = np.array(self.init_state['pos'], dtype=np.int8)
        self.heading = self.init_state['heading'] 

    def signal_reached_goal(self):
        """Sent by the controller when mouse reaches goal.
        """
        self.reached_goal = True

    def signal_end_run(self):
        """Sent by the controller when run ends.
        
        Run could end due to successfully reaching centre, or timeout.
        """
        self.reset_state()

