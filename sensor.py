import pdb
from enum import Enum
import numpy as np
from rotation import Rotation

class Sensor(Enum):
    LEFT = 0
    FORWARD = 1
    RIGHT = 2

    def rotation(sensor):
        """Returns the rotation of a sensor.

        Arguments:
            sensor -- the Sensor, e.g. Sensor.RIGHT.
        Returns:
            the Rotation of the sensor.
        """
        # Return the sensor rotation.
        return Sensor.__sensor_rotation_map()[sensor]

    def __sensor_rotation_map():
        """Maps from sensor to rotation.
        """
        return {
            Sensor.LEFT: Rotation.LEFT,
            Sensor.FORWARD: Rotation.NONE,
            Sensor.RIGHT: Rotation.RIGHT
        }

    def node_sensed(readings):
        """
        Looks like a node if the left or right sensor-readings are non-zero, or
        we're at a dead-end and all readings are zero.

        Makes assumptions that there is an exit behind us.
        """
        # Get sensors leading to exits.
        exits = np.nonzero(readings)[0]

        # If sensor readings are all blank, we're at a node.
        if len(exits) == 0:
            return True

        # If left or right passages are exits, we're at a node. This is because,
        # assuming there is a passage behind us, there is an l-bend at this
        # square.
        if Sensor.LEFT.value in exits or Sensor.RIGHT.value in exits:
            return True

        return False

