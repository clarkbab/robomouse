import turtle
import numpy as np
import pdb
from heading import Heading

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
        self.paths = np.zeros((maze.dim ** 2, maze.dim ** 2), dtype=np.int8)
        
        # For some reason turtle crashes when we reboot the screen..
        try:
            turtle.Turtle()
        except turtle.Terminator:
            pass

        # Set North to 0 degrees.
        turtle.mode('logo')

        # Create the screen. 
        self.screen = turtle.Screen()
        self.screen.title('RoboMouse')

        # Create the index tool.
        self.index_tool = turtle.Turtle()
        self.index_tool.hideturtle()
        self.index_tool.pensize(3)
        self.index_tool.color('blue')

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

        self.draw_indexes()

        # Draw walls of maze.
        for x in range(self.maze.dim):
            for y in range(self.maze.dim):
                if not self.maze.is_permissible([x, y], Heading.NORTH):
                    self.draw_wall((x, y), Heading.NORTH)

                if not self.maze.is_permissible([x, y], Heading.EAST):
                    self.draw_wall((x, y), Heading.EAST)

                # We don't need to draw walls twice, so only check 'down' and
                # 'left' if we're at the bottom or on the far left.
                if y == 0 and not self.maze.is_permissible([x, y], Heading.SOUTH):
                    self.draw_wall((x, y), Heading.SOUTH)

                # Same as above, don't check 'left' unless at far left.
                if x == 0 and not self.maze.is_permissible([x, y], Heading.WEST):
                    self.draw_wall((x, y), Heading.WEST)

        # Turn animation back on.
        self.screen.tracer(1)

    def draw_indexes(self):
        # Draw x axis.
        y_loc = self.origin - self.square_size
        for i in range(self.maze.dim):
            x_loc = self.origin + (i + 0.5) * self.square_size
            self.index_tool.penup()
            self.index_tool.goto(x_loc, y_loc)
            self.index_tool.pendown()
            self.index_tool.write(i, False, align='center', font=('Arial', 24, 'normal'))

        # Draw y axis.
        x_loc = self.origin - (2 / 3) * self.square_size
        for i in range(self.maze.dim):
            y_loc = self.origin + i * self.square_size
            self.index_tool.penup()
            self.index_tool.goto(x_loc, y_loc)
            self.index_tool.pendown()
            self.index_tool.write(i, False, align='center', font=('Arial', 24, 'normal'))


    def draw_wall(self, cell, side):
        """Draws a wall for a cell.

        Arguments:
            cell -- the position of the cell.
            side -- the heading of the wall.
        """
        # Get the starting point and direction for the line.
        start = None
        heading = None
        if side == Heading.NORTH:
            start = (self.origin + self.square_size * cell[0], self.origin +
                self.square_size * (cell[1] + 1))
            heading = Heading.EAST 
        elif side == Heading.EAST:
            start = (self.origin + self.square_size * (cell[0] + 1), self.origin
                + self.square_size * cell[1])
            heading = Heading.NORTH
        elif side == Heading.SOUTH:
            start = (self.origin + self.square_size * cell[0], self.origin +
                self.square_size * cell[1])
            heading = Heading.EAST
        elif side == Heading.WEST:
            start = (self.origin + self.square_size * cell[0], self.origin + self.square_size * cell[1])
            heading = Heading.NORTH

        # Draw the line.
        self.maze_tool.penup()
        self.maze_tool.goto(*start)
        self.maze_tool.setheading(heading.value)
        self.maze_tool.pendown()
        self.maze_tool.forward(self.square_size)
        self.maze_tool.penup()

    def place_mouse(self, pos, heading):
        """Places the mouse in the maze.

        Arguments:
            pos -- the mouse's position. a list containing x, y integer co-ordinates. 
            heading -- a Heading value, e.g. Heading.NORTH.
        """
        # Keep track of pos for path drawing.
        self.pos = np.array(pos, dtype=np.int8)

        # Set the mouse location.
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.mouse_tool.penup()
        self.mouse_tool.goto(x, y)

        # Set the heading.
        self.mouse_tool.setheading(heading.value)

        # Put the pen down ready for drawing.
        self.mouse_tool.pendown()

    def set_heading(self, heading):
        """Draws a new heading for the mouse.

        Arguments:
            heading -- a Heading value, e.g. Heading.NORTH.
        """
        # Set the mouse's heading.
        self.mouse_tool.setheading(heading.value)

    def increment_path(self, from_pos, to_pos):
        # Convert the positions to indexes.
        from_idx, to_idx = self.square_index(from_pos), self.square_index(to_pos)

        # Increment the path in both directions.
        self.paths[from_idx, to_idx] += 1
        self.paths[to_idx, from_idx] += 1

        return self.paths[from_idx, to_idx]

    def square_index(self, pos):
        return pos[0] + self.maze.dim * pos[1]

    def move(self, pos):
        """Draws a mouse's move.

        Arguments:
            pos -- the mouse's position. a list containing x, y integer co-ordinates. 
        """
        # Get x, y coordinates.
        old_pos = self.pos.copy()
        x = self.origin + (pos[0] + 0.5) * self.square_size
        y = self.origin + (pos[1] + 0.5) * self.square_size
        self.pos = np.array(pos, dtype=np.int8)
        
        # Calculate the heading, and number of steps.
        diff = self.pos - old_pos
        n_squares = np.linalg.norm(diff)
        heading = np.array(diff / n_squares, dtype=np.int8)

        # For each square, draw the colour corresponding to how many times we've
        # taken that path.
        for i in range(int(n_squares)):
            # Get old and new pos for each step.
            start_pos = old_pos + i * heading
            end_pos = old_pos + (i + 1) * heading

            # Increment the path counter.
            n = self.increment_path(start_pos, end_pos)

            # Set path colour.
            colour = 'red'
            if n == 2:
                colour = 'orange'
            elif n == 3:
                colour = 'yellow'
            elif n == 4:
                colour = 'green'
            elif n == 5:
                colour = 'blue'
            elif n > 5:
                colour = 'violet'
            
            # Draw path.
            self.mouse_tool.color(colour)
            self.mouse_tool.goto(x, y)

    def clear_track(self):
        """Clears the mouse's tracks from the display.
        """
        self.mouse_tool.clear()
        self.paths = np.zeros((self.maze.dim ** 2, self.maze.dim ** 2), dtype=np.int8)

    def mainloop(self):
        """Begins the Turtle mainloop.

        This loop can only be broken using the 'Display.close()' method.
        """
        turtle.mainloop()
        
    def close(self):
        """Closes the display.
        """
        print('closing screen')
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

