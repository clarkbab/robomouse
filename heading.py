from enum import Enum
import numpy as np

class Heading(Enum):
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

    def rotate(heading, rot):
        """Returns a new heading, rotated by the specified amount.

        Arguments:
            heading -- a Heading, e.g. Heading.NORTH.
            rot -- a rotation, e.g. Rotation.LEFT.
        Returns:
            the new Heading.
        """
        # Get the new heading.
        new_value = heading.value + rot.value

        # Wrap heading around if necessary.
        if new_value < 0:
            new_value += 360
        elif new_value >= 360:
            new_value -= 360

        return Heading(new_value)

    def opposite(heading):
        """Returns the opposite heading.

        Arguments:
            heading -- a Heading, e.g. Heading.NORTH.
        Returns:
            the opposite Heading.
        """
        # Get the heading value.
        new_value = heading.value

        # Rotate by half a circle.
        new_value += 180

        # Wrap if necessary.
        if new_value >= 360:
            new_value -= 360

        return Heading(new_value)

    def components(heading):
        """Returns the vector components of the heading.
        """
        return Heading.__heading_components_map()[heading]

    def from_components(components):
        """Returns the heading from the components.
        """
        # Return the heading with these components.  
        return next(h for h, c in Heading.__heading_components_map().items() if np.array_equal(c, components))

    def __heading_components_map():
        return {
            Heading.NORTH: np.array([0, 1]),
            Heading.EAST: np.array([1, 0]), 
            Heading.SOUTH: np.array([0, -1]),
            Heading.WEST: np.array([-1, 0])
        }

        
