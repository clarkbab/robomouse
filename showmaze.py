from maze import Maze
import turtle
import sys
import pdb
import time

if __name__ == '__main__':
    '''
    This function uses Python's turtle library to draw a picture of the maze
    given as an argument when running the script.
    '''

    # Create a maze based on input argument on command line.
    testmaze = Maze( str(sys.argv[1]) )

    # Intialize the screen and drawing turtle.

                
    # Move to start.
    wally.goto(origin + sq_size / 2, origin + sq_size / 2)
    wally.setheading(90)
    wally.pendown()

    # Slow down the turtle's movements and draw every update.
    screen.delay(10)
    wally.showturtle()
    wally.speed('slowest')

    # Create the state machine.
    def move():
        wally.forward(sq_size)
        

    machine = StateMachine(move)
        
    # Add screen event handlers.
    screen.onkey(machine.toggle_pause, 'space')
    screen.onkey(lambda: screen.bye(), 'q')
    screen.listen()
    
    # Run the state machine.
    machine.run(screen)

    # Start main loop.
    turtle.mainloop()

