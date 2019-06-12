import pdb
from enum import Enum
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

