import numpy as np

class Maze(object):
    # Define the directions.
    NORTH = 0
    EAST = 90
    SOUTH = 180
    WEST = 270

    # Acceptable heading range.
    HEADING_RANGE = range(360)
    
    # Maps headings to the axial components.
    HEADING_COMPONENTS_MAP = {
        NORTH: np.array([0, 1]),
        EAST: np.array([1, 0]),
        SOUTH: np.array([0, -1]),
        WEST: np.array([-1, 0])
    }

    # Maps heading to wall decimal.
    HEADING_DECIMAL_MAP = {
        NORTH: 1,
        EAST: 2,
        SOUTH: 4,
        WEST: 8
    }

    def __init__(self, filename):
        """Reads in a maze file.

        Maze objects have two main attributes:
        - dim: mazes should be square, with sides of even length. (integer)
        - walls: passages are coded as a 4-bit number, with a bit value taking
            0 if there is a wall and 1 if there is no wall. The 1s register
            corresponds with a square's top edge, 2s register the right edge,
            4s register the bottom edge, and 8s register the left edge. (numpy
            array)

        The initialization function also performs some consistency checks for
        wall positioning.

        Arguments:
            filename -- the path to the maze file.
        """
        with open(filename, 'r') as f_in:
            # Read lines of file.
            lines = [line for line in f_in]

            # First line should be an integer with the maze dimensions
            self.dim = int(lines[0])

            # Subsequent lines describe the permissability of walls
            walls = []
            for line in lines[1:]:
                walls.append(list(map(int, line.strip().split(','))))
            self.walls = np.array(walls)

        # Perform validation on maze
        # Maze dimensions
        if self.dim % 2:
            raise Exception('Maze dimensions must be even in length!')
        if self.walls.shape != (self.dim, self.dim):
            raise Exception('Maze shape does not match dimension attribute!')

        # Wall permeability
        wall_errors = []
        # vertical walls
        for x in range(self.dim-1):
            for y in range(self.dim):
                if (self.walls[x,y] & 2 != 0) != (self.walls[x+1,y] & 8 != 0):
                    wall_errors.append([(x,y), 'v'])
        # horizontal walls
        for y in range(self.dim-1):
            for x in range(self.dim):
                if (self.walls[x,y] & 1 != 0) != (self.walls[x,y+1] & 4 != 0):
                    wall_errors.append([(x,y), 'h'])

        if wall_errors:
            for cell, wall_type in wall_errors:
                if wall_type == 'v':
                    cell2 = (cell[0]+1, cell[1])
                    print(f"Inconsistent vertical wall betweeen {cell} and {cell2}")
                else:
                    cell2 = (cell[0], cell[1]+1)
                    print(f"Inconsistent horizontal wall betweeen {cell} and {cell2}")
            raise Exception('Consistency errors found in wall specifications!')

    def is_permissible(self, pos, heading):
        """Tells if we can move from a square in a heading.

        Arguments:
            pos -- the current position.
            heading -- the heading to move in.
        Returns:
            True if we can move, False otherwise.
        """
        # Check if there's a wall in that direction.
        return self.walls[pos[0], pos[1]] & self.HEADING_DECIMAL_MAP[heading] != 0

    def dist_to_wall(self, pos, heading):
        """Checks the distance to a wall in a particular heading.

        Arguments:
            pos -- the current position.
            heading -- the current heading.
        Return:
            an integer distance. The number of moves that can be made in that direction.
        """
        # Copy the pos as we're modifying it.
        curr_pos = pos.copy()

        distance = 0
        while self.is_permissible(curr_pos, heading):
            distance += 1
            curr_pos[0] += self.HEADING_COMPONENTS_MAP[heading][0]
            curr_pos[1] += self.HEADING_COMPONENTS_MAP[heading][1]

        return distance

    def new_pos(self, pos, heading, move):
        """Returns the new position after moving.

        Arguments:
            pos -- the current position.
            heading -- the current heading.
            move -- the desired move.
        Returns:
            A list of [x, y] int components, showing the new position.
        """
        # Get x, y changes.
        dx, dy = move * self.HEADING_COMPONENTS_MAP[heading] 

        # Update x, y co-ordinates.
        x_new, y_new = pos[0] + dx, pos[1] + dy

        return [int(x_new), int(y_new)]

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
        
    def sensor_readings(self, pos, heading):
        """Calculate the mouse's sensor readings.

        Arguments:
            pos -- the mouse's current position.
            heading -- the mouse's heading.
        Returns:
            A tuple of sensor readings, each giving the distance to the wall in the (left, middle, right) directions.
        """
        # Get left and right headings.
        l_head = self.new_heading(heading, -90)
        r_head = self.new_heading(heading, 90)

        # Get distances for each heading.
        dist = self.dist_to_wall(pos, heading)
        l_dist = self.dist_to_wall(pos, l_head) 
        r_dist = self.dist_to_wall(pos, r_head) 

        return (l_dist, dist, r_dist)

    def reached_goal(self, pos):
        """Is the position within the goal?

        Arguments:
            pos -- the position.
        Returns:
            True if goal reached, else False.
        """
        # Both axes will have the same goal co-ordinates.
        goal_coords = [self.dim / 2 -1, self.dim / 2]

        # Check if position in goal.
        if not (pos[0] in goal_coords and pos[1] in goal_coords):
            return False

        return True

    def valid_move(self, pos, heading, size):
        """Checks if the mouse's move is valid in the context of the maze.

        Arguments:
            pos -- the [x, y] co-ordinates of the mouse.
            heading -- the heading of the movement. This isn't necessarily the  heading of the mouse, it could be
                reversing.
            size -- the size of the move. Positive or negative.
        Returns:
            True if valid move, False otherwise.
        """
        # Check that starting pos is valid.
        if not self.pos_exists(pos):
            return False
            
        # Get the move direction. Positive or negative. 
        move_heading = heading
        dir = (-1, 1)[size > 0]
        if dir == -1:
            move_heading += 180
            if move_heading >= 360:
                move_heading -= 360

        # Get distance to the wall.
        dist = self.dist_to_wall(pos, move_heading)

        # Is the move size larger than the distance to the wall?
        if abs(size) > dist:
            return False

        return True
            
    def pos_exists(self, pos):
        """Checks if this is a valid position in the maze.

        Arguments:
            pos -- a list containing the [x, y] co-ordinates of the mouse.
        Returns:
            True if position exists, False otherwise.
        """
        # Check that position is integer.
        if not isinstance(pos[0], int) or not isinstance(pos[1], int):
            return False

        # Check against maze dimensions.
        if not (pos[0] >= 0 and pos[0] < self.dim) or not (pos[1] >= 0 and
            pos[1] < self.dim):
            return False

        return True

