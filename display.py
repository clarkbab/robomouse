import turtle
import pdb

class Display:
    def __init__(self, maze, square_size=20):
        self.maze = maze
        self.square_size = square_size
        self.origin = maze.dim * square_size / -2

        # Set North to 0 degrees.
        turtle.mode('logo')

        # Create the screen. 
        self.screen = turtle.Screen()
        self.screen.title('RoboMouse')

    def draw_maze(self):
        """Draws the maze structure.
        """
        # Create the drawing tool.
        self.tool = turtle.Turtle()
        self.tool.pensize(3)
        self.tool.hideturtle()
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

        # Turn tracer back on.
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

        self.tool.penup()
        self.tool.goto(*start)
        self.tool.setheading(heading)
        self.tool.pendown()
        self.tool.forward(self.square_size)
        self.tool.penup()

    def place_mouse(self, pos, heading):
        """places the mouse in the maze.

        arguments:
            pos -- the position to place. a tuple containing position of mouse
                on board from 0 to maze (dim - 1).
            heading -- the heading the mouse has. a value in degrees from 0
                (right) to 360, counter-clockwise.
        """
        # Create the mouse drawing cursor.
        self.mouse = turtle.Turtle()
        self.mouse.pensize(2)
        self.mouse.color('red')
        self.mouse.penup()

        # Set the mouse location.
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.mouse.goto(x, y)

        # Set the heading.
        self.mouse.setheading(heading)

        # Put the pen down ready for drawing.
        self.mouse.pendown()

    def set_heading(self, heading):
        # Set the mouse's heading.
        self.mouse.setheading(heading)

    def move(self, pos):
        # Get x, y coordinates.
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.mouse.goto(x, y)

    def listen(self, callback, period):
        """sets focus on the turtlescreen and listens for events.
        """
        # set up timer that will kick off iterations.
        self.sleep(callback, period)
        
        # start listening for events and running the gui mainloop.
        self.screen.listen()
        turtle.mainloop()

    def sleep(self, callback, period):
        print('queueing timer with delay: {}'.format(period))
        self.screen.ontimer(callback, period)

