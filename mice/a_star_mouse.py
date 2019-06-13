import pdb
import numpy as np
from heading import Heading
from rotation import Rotation
from sensor import Sensor
from state import State
from phase import Phase
from graph import Graph

class AStarMouse():
    MAX_MOVE = 3

    def __init__(self, maze_dim, init_state, verbose):
        # Initialise the state.
        self.state = State(init_state['pos'], init_state['heading'])

        # Store maze dimensions to calculate unique square IDs.
        self.maze_dim = maze_dim

        # Calculate maze centre for magnetism.
        self.maze_centre = np.array([(maze_dim - 1) / 2, (maze_dim - 1) / 2])

        # Start in planning mode.
        self.phase = Phase.PLAN

        # Initialise flags.
        self.initialising = True
        self.backtrack = False
        self.reading = None
        self.reached_goal = False
        self.verbose = verbose

        # Create the graph.
        self.graph = Graph()

    def unit_centre(self):
        """Finds the unit vector from the mouse to the centre.
        """
        vec = self.maze_centre - self.state.pos
        unit_vec = vec / np.linalg.norm(vec)
        return unit_vec

    def softmax(self, values):
        """Performs the softmax function on the list of input values.
        """
        # Shift the values so the maximum is zero.
        shift_values = values - np.max(values)
        return np.exp(shift_values) / np.sum(np.exp(shift_values))

    def square_id(self, pos):
        """Generates a unique ID for the square.
        """
        return pos[0] + self.maze_dim * pos[1]

    def next_move(self, readings):
        # Print mouse's assumed location.
        if self.verbose:
            print(f"[MOUSE] Phase: {self.phase.value}")
            print(f"[MOUSE] Pos: {self.state.pos}")
            print(f"[MOUSE] Heading: {self.state.heading}")

        # Get the mouse's next move.
        rot, move = self.plan_move(readings)

        # Update the mouse's internal state.
        if not (rot, move) == ('RESET', 'RESET'):
            self.state.update(rot, move)

        # check if we're in the goal.
        if self.in_goal():
            self.reached_goal = True
            if self.verbose:
                print(f"[MOUSE] reached goal.")

            if self.phase == Phase.EXECUTE:
                if self.verbose: print(f"[MOUSE] finished.")

        return rot, move

    def in_goal(self):
        """Checks if we're in the centre of the maze.
        """
        # Both axes will have the same goal co-ordinates.
        goal_coords = [self.maze_dim / 2 - 1, self.maze_dim / 2]

        # Check if position in goal.
        if not (self.state.pos[0] in goal_coords and self.state.pos[1] in goal_coords):
            return False

        return True

    def square_position(self, square_id):
        """Gets the position of a square.
        """
        # Get x, y coordinates.
        x = square_id % self.maze_dim
        y = int(square_id / self.maze_dim)

        return np.array([x, y])

    def edge_move(self, edge):
        """Gets the largest move we can make down the known edge.
        """
        # Get the destination node.
        node_pos = self.square_position(edge['node'])

        # How do we travel to get there?
        diff = node_pos - self.state.pos

        # Get the largest move we can make in that direction.
        return int(min(np.linalg.norm(diff), self.MAX_MOVE))

    def plan_move(self, readings):
        # Get the ID of the current square.
        square_id = self.square_id(self.state.pos)

        # If we're executing, follow the path.
        if self.phase == Phase.EXECUTE:
            # Get the destination node.
            node = self.path[0]

            # Are we actually at the next destination node?
            if square_id == node:
                # Track the last node we visited so we know which edge we're on.
                self.last_node = node

                # Update the path and destination.
                self.path = self.path[1:]
                node = self.path[0]

            # Find edge to travel down.
            edge = self.graph.find_edge_by_nodes(self.last_node, node)

            # Compare the current heading to desired heading.
            rot = None
            for rotation in Rotation:
                if Heading.rotate(self.state.heading, rotation) == edge['heading']:
                    rot = rotation

            # Can't make it there in one rotation.
            if rot is None:
                return Rotation.LEFT, 0 
            
            # Get the largest move we can make in that direction.
            move = self.edge_move(edge)

            return rot, move

        # If it's our first move, mark the square as a node and pick an exit or
        # rotate.
        if self.initialising:
            self.initialising = False
            self.graph.add_node(square_id)
            self.last_node = square_id

            # Get all the exits.
            exits = np.nonzero(readings)[0]

            # If no exits, rotate.
            if len(exits) == 0:
                return Rotation.LEFT, 0

            # Pick the first exit.
            sensor = Sensor(exits[0])
            rot = Sensor.rotation(sensor)
            return rot, 1

        # Check if we're backtracking.
        if self.backtrack:
            self.backtrack = False

            # Get the direction we're moving in.
            move_heading = Heading.rotate(self.state.heading, Rotation.LEFT)

            # Load up the edge we'll be travelling on.
            edge = self.graph.find_edge_by_heading(square_id, move_heading)

            # What's the largest move we can make down this edge?
            move = self.edge_move(edge)

            return Rotation.LEFT, move

        # If it's not a node, just move forward.
        if not Sensor.node_sensed(readings):
            # Get the edge we're currently on.
            edge = self.graph.find_edge_by_heading(self.last_node, self.state.heading)

            # If we're on an edge, move further if possible.
            move = self.edge_move(edge) if edge else 1

            return Rotation.NONE, move
        
        # At this point we've decided that the square is a node.

        # Add the node if it hasn't been already.
        node_already_added = self.graph.node_added(square_id)
        if not node_already_added:
            # Add the node.
            self.graph.add_node(square_id)

        # We're turning around on the spot, don't need to add an edge.
        if square_id != self.last_node:
            # Check if edge already exists.
            if not self.graph.find_edge_by_nodes(self.last_node, square_id):
                # Get positions of nodes.
                node_pos1 = self.square_position(self.last_node)
                node_pos2 = self.square_position(square_id)

                # Get distance between nodes.
                vec = node_pos2 - node_pos1
                dist = int(np.linalg.norm(vec))

                # Get headings traversing from node 1 to 2, and reverse.
                head_vect = vec / dist 
                heading = Heading.from_components(head_vect)

                # Add the new edge.
                self.graph.add_edge(self.last_node, square_id, dist, heading)
            else:
                # Increment the number of traversals for this edge.
                self.graph.increment_traversal(self.last_node, square_id)

        # Check if we should reset.
        if self.phase == Phase.PLAN and self.reached_goal:
            if self.verbose: print(f"[MOUSE] Finished planning.")

            # Get the start and end nodes.
            start_node = self.square_id(self.state.init_pos)
            end_node = square_id

            # Find the shortest path from start to finish. Remove first node as
            # we're starting there.
            self.path = self.graph.shortest_path(start_node, end_node, self.heuristic_cost)

            # Begin execution phase.
            self.phase = Phase.EXECUTE
            self.state.reset()
            return 'RESET', 'RESET'

        # Get a prob for each direction.
        sensors = np.array([], dtype=np.int8)
        weights = np.array([], dtype=np.float32)
        traversals = np.array([], dtype=np.int8)
        move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for i, reading in enumerate(readings):
            # Don't consider the move if we'll hit a wall.
            if reading == 0: continue

            # Create the Sensor.
            sensor = Sensor(i)

            # Get the edge we'll be traversing if we take this move.
            sensor_heading = Heading.rotate(self.state.heading, Sensor.rotation(sensor))
            edge = self.graph.find_edge_by_heading(square_id, sensor_heading)

            # Get number of traversals. 0 if edge isn't recorded.
            traversal = edge['traversals'] if edge else 0

            # Don't take the edge if we've been there twice already.
            if traversal > 1:
                continue

            # If we're on an edge, we can possibly move faster.
            move = self.edge_move(edge) if edge else 1

            # Get the move vector components.
            move_vec = move * Heading.components(sensor_heading)
            
            # Add the number of edge traversals.
            traversals = np.append(traversals, traversal)

            # Add the move vec and sensor ID.
            move_vecs = np.vstack((move_vecs, move_vec))
            sensors = np.append(sensors, sensor)

            # How much of this move is towards the centre?
            weight = np.dot(move_vec, self.unit_centre())
            weights = np.append(weights, weight)

        # If no possible moves, let's turn around.
        if len(move_vecs) == 0:
            self.last_node = square_id
            return Rotation.LEFT, 0

        # If we're not turning on the spot, and we've already seen the node.
        if self.last_node != square_id and node_already_added:
            # If we only traversed the last edge once, go back that way. We've
            # reached the end of a branch in our depth-first search algorithm.
            num_traversals = self.graph.find_edge_by_nodes(self.last_node, square_id)['traversals']
            if num_traversals == 1:
                self.last_node = square_id
                self.backtrack = True
                return Rotation.LEFT, 0

        # Take the road less travelled, i.e, select those squares that we've visited less.
        min_idx = np.argwhere(traversals == np.min(traversals)).flatten()

        # Only keep edges with minimum traversals.
        sensors = sensors[min_idx]
        weights = weights[min_idx]
        move_vecs = move_vecs[min_idx]

        # Apply the softmax function.
        probs = self.softmax(weights)
        
        # Get a sensor based on the probs.
        sensor = np.random.choice(sensors, p=probs)
        idx = np.where(sensors == sensor)[0][0]

        # Get the rotation and move to perform.
        rot = Sensor.rotation(sensor)
        move_vec = move_vecs[idx]
        move = abs(move_vec).max()
        
        # Update internal state.
        self.last_node = square_id
        
        # The last thing we do is update our state. We don't know anything about
        # the next square at this point; this info will be handed to us with the
        # next sensor reading. So it doesn't make any sense to start working on
        # adding the next node or anything. In fact, we don't know if this step
        # will bring us to a node or a passage until we get sensor readings.

        return rot, move

    def heuristic_cost(self, start_node, end_node):
        # Get start and end node positions.
        start_pos, end_pos = self.square_position(start_node), self.square_position(end_node)

        # Calculate the min steps required in each direction.
        diff = np.abs(end_pos - start_pos)
        x_min = np.ceil(diff[0] / self.MAX_MOVE)
        y_min = np.ceil(diff[1] / self.MAX_MOVE) 

        # Return the sum of moves.
        return x_min + y_min

