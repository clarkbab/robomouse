import turtle
import pdb

class Display:
    def __init__(self, maze, square_size=30):
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

        self.maze_tool.penup()
        self.maze_tool.goto(*start)
        self.maze_tool.setheading(heading)
        self.maze_tool.pendown()
        self.maze_tool.forward(self.square_size)
        self.maze_tool.penup()

    def place_mouse(self, pos, heading):
        """places the mouse in the maze.

        arguments:
            pos -- the position to place. a tuple containing position of mouse
                on board from 0 to maze (dim - 1).
            heading -- the heading the mouse has. a value in degrees from 0
                (right) to 360, counter-clockwise.
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
        # Set the mouse's heading.
        self.mouse_tool.setheading(heading)

    def move(self, pos):
        # Get x, y coordinates.
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.mouse_tool.goto(x, y)

    def listen(self, callback, period):
        """sets focus on the turtlescreen and listens for events.
        """
        # set up timer that will kick off iterations.
        self.sleep(callback, period)
        
        # start listening for events and running the gui mainloop.
        self.screen.listen()
        turtle.mainloop()

    def close(self):
        turtle.bye()

    def sleep(self, callback, period):
        self.screen.ontimer(callback, period)

    def clear_track(self):
        self.mouse_tool.clear()

