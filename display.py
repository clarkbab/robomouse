import turtle
import pdb

class Display:
    def __init__(self, maze, square_size=30):
        """Constructs the maze display.

        Arguments:
            maze -- the Maze to show.
            square_size -- the width of each square in the Maze.
        """
        self.maze = maze
        self.square_size = square_size
        self.origin = maze.dim * square_size / -2

        # Set North to 0 degrees.
        turtle.mode('logo')

        # Create the screen. 
        self.screen = turtle.Screen()
        self.screen.title('RoboMouse')

        # Create the maze drawing tool.
        self.maze_tool = turtle.Turtle()
        self.maze_tool.pensize(3)
        self.maze_tool.hideturtle()

        # Create the mouse drawing tool.
        self.mouse_tool = turtle.Turtle()
        self.mouse_tool.pensize(2)
        self.mouse_tool.color('red')

    def draw_maze(self):
        """Draws the maze structure.

        Animation is turned off for this step, so it will happen instantaneously. 
        """
        # Turn animation off to draw maze instantaneously.
        self.screen.tracer(0)

        # Draw walls of maze.
        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                if not self.maze.is_permissible([x, y], self.maze.NORTH):
                    self.draw_wall((x, y), self.maze.NORTH)

                if not self.maze.is_permissible([x, y], self.maze.EAST):
                    self.draw_wall((x, y), self.maze.EAST)

                # We don't need to draw walls twice, so only check 'down' and
                # 'left' if we're at the bottom or on the far left.
                if y == 0 and not self.maze.is_permissible([x, y], self.maze.SOUTH):
                    self.draw_wall((x, y), self.maze.SOUTH)

                # Same as above, don't check 'left' unless at far left.
                if x == 0 and not self.maze.is_permissible([x, y], self.maze.WEST):
                    self.draw_wall((x, y), self.maze.WEST)

        # Turn animation back on.
        self.screen.tracer(1)

    def draw_wall(self, cell, side):
        """Draws a wall for a cell.

        Arguments:
            cell -- the position of the cell.
            side -- the heading of the wall.
        """
        # Get the starting point and direction for the line.
        start = None
        heading = None
        if side == self.maze.NORTH:
            start = (self.origin + self.square_size * cell[0], self.origin +
                self.square_size * (cell[1] + 1))
            heading = self.maze.EAST
        elif side == self.maze.EAST:
            start = (self.origin + self.square_size * (cell[0] + 1), self.origin
                + self.square_size * cell[1])
            heading = self.maze.NORTH
        elif side == self.maze.SOUTH:
            start = (self.origin + self.square_size * cell[0], self.origin +
                self.square_size * cell[1])
            heading = self.maze.EAST
        elif side == self.maze.WEST:
            start = (self.origin + self.square_size * cell[0], self.origin + self.square_size * cell[1])
            heading = self.maze.NORTH

        # Draw the line.
        self.maze_tool.penup()
        self.maze_tool.goto(*start)
        self.maze_tool.setheading(heading)
        self.maze_tool.pendown()
        self.maze_tool.forward(self.square_size)
        self.maze_tool.penup()

    def place_mouse(self, pos, heading):
        """Places the mouse in the maze.

        Arguments:
            pos -- the mouse's position. a list containing x, y integer co-ordinates. 
            heading -- the mouse's heading. an integer in the range (0, 360].
        """

        # Set the mouse location.
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.mouse_tool.penup()
        self.mouse_tool.goto(x, y)

        # Set the heading.
        self.mouse_tool.setheading(heading)

        # Put the pen down ready for drawing.
        self.mouse_tool.pendown()

    def set_heading(self, heading):
        """Draws a new heading for the mouse.

        Arguments:
            heading -- the mouse's heading. an integer in the range (0, 360].
        """
        # Set the mouse's heading.
        self.mouse_tool.setheading(heading)

    def move(self, pos):
        """Draws a mouse's move.

        Arguments:
            pos -- the mouse's position. a list containing x, y integer co-ordinates. 
        """
        # Get x, y coordinates.
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.mouse_tool.goto(x, y)

    def clear_track(self):
        """Clears the mouse's tracks from the display.
        """
        self.mouse_tool.clear()

    def mainloop(self):
        """Begins the Turtle mainloop.

        This loop can only be broken using the 'Display.close()' method.
        """
        turtle.mainloop()
        
    def close(self):
        """Closes the display.
        """
        turtle.bye()

    def on_space(self, callback):
        """Registers a callback to run on 'space' event on display.

        Arguments:
            callback -- a function to run on 'space' press.
        """
        self.screen.onkey(callback, 'space')

    def sleep(self, callback, delay):
        """Registers a callback to run after some delay.

        Arguments:
            callback -- the function to run after delay.
            delay -- the delay in ms.
        """
        self.screen.ontimer(callback, delay)


