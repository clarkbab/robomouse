import pdb
import numpy as np
from heading import Heading
from rotation import Rotation
from sensor import Sensor
from state import State
from phase import Phase

class TremauxMouse():
    MAX_MOVE = 3

    def __init__(self, maze_dim, init_state, verbose):
        # Initialise the state.
        self.state = State(init_state['pos'], init_state['heading'])
        self.maze_centre = np.array([(maze_dim - 1) / 2, (maze_dim - 1) / 2])
        self.backtrack = False

        # Need this for initial steps.
        self.initialising = True
        self.reading = None

        # Create dict of nodes and edges.
        self.nodes = dict()

    def unit_centre(self):
        """Finds the unit vector from the mouse to the centre.
        """
        vec = self.maze_centre - self.pos
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
            print(f"[MOUSE] Pos: {self.pos}")
            print(f"[MOUSE] Heading: {self.heading.value}")

        # Get the mouse's next move.
        rot, move = self.plan_move(readings)

        # Update the mouse's internal state.
        if not (rot, move) == ('RESET', 'RESET'):
            self.update_state(rot, move)

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

    def find_edge_by_nodes(self, node1, node2):
        """Gets the edge between two nodes.
        """
        return next((e for e in self.nodes[node1] if e['node'] == node2), None)

    def find_edge_from_node(self, node, heading):
        """Gets an edge radiating out from a node.
        """
        return next((e for e in self.nodes[node] if e['heading'] == heading), None)

    def edge_move(self, edge):
        """Gets the largest move we can make down the known edge.
        """
        # Get the destination node.
        node_pos = self.square_position(edge['node'])

        # How do we travel to get there?
        diff = node_pos - self.pos

        # Get the largest move we can make in that direction.
        return int(min(np.linalg.norm(diff), self.MAX_MOVE))

    def add_edge(self, node1, node2):
        # Get positions of nodes.
        node_pos1 = self.square_position(node1)
        node_pos2 = self.square_position(node2)

        # Get distance between nodes.
        vec = node_pos2 - node_pos1
        dist = int(np.linalg.norm(vec))

        # Get headings traversing from node 1 to 2, and reverse.
        head_vect = vec / dist 
        heading1 = Heading.from_components(head_vect)
        heading2 = Heading.opposite(heading1)

        # Add connections.
        edge1 = { 'node': node2, 'length': dist, 'heading': heading1, 'traversals': 1 }
        edge2 = { 'node': node1, 'length': dist, 'heading': heading2, 'traversals': 1 }
        self.nodes[node1] = np.append(self.nodes[node1], edge1)
        self.nodes[node2] = np.append(self.nodes[node2], edge2)

    def increment_traversal(self, node1, node2):
        # Load the edges.
        edge1 = self.find_edge_by_nodes(node1, node2)
        edge2 = self.find_edge_by_nodes(node2, node1)

        # Increment the traversals.
        edge1['traversals'] += 1
        edge2['traversals'] += 1

    def node_added(self, node):
        return node in self.nodes

    def node_sensed(self, readings):
        """
        Looks like a node if the left or right sensor-readings are non-zero, or
        we're at a dead-end and all readings are zero.

        Makes assumptions that there is an exit behind us.
        """
        # Get exits from non-zero sensor readings.
        exits = np.nonzero(readings)[0]

        # If there are no exits, we're at a dead-end, which is a node.
        if len(exits) == 0:
            return True

        # If left or right passages are exits, we're at a node. This is because,
        # assuming there is a passage behind us, there is an l-bend at this
        # square.
        if Sensor.LEFT.value in exits or Sensor.RIGHT.value in exits:
            return True

        return False

    def add_node(self, node):
        # Record the node.
        self.nodes[node] = np.array([])

    def get_edge(self, node, heading):
        return next((e for e in self.nodes[node] if e['heading'] == heading), None)

    def plan_move(self, readings):
        # Get the ID of the current square.
        square_id = self.square_id(self.pos)

        # If it's our first move, mark the square as a node and pick an exit or
        # rotate.
        if self.initialising:
            self.initialising = False
            self.add_node(square_id)
            self.last_node = square_id

            # Get all the exits.
            exits = np.nonzero(readings)[0]

            # If no exits, rotate.
            if len(exits) == 0:
                return -90, 0

            # Pick the first exit.
            sensor = Sensor(exits[0])
            rot = Sensor.rotation(sensor)
            return rot, 1

        # Check if we should reset.
        if self.reached_goal:
            if self.verbose: print(f"[MOUSE] Finished planning.")
            self.start_execution()
            self.initialising = True
            self.nodes = dict()
            return 'RESET', 'RESET'

        # Check if we're backtracking.
        if self.backtrack:
            self.backtrack = False

            # Get the direction we're moving in.
            move_heading = Heading.rotate(self.heading, Rotation.LEFT)

            # Load up the edge we'll be travelling on.
            edge = self.find_edge_from_node(square_id, move_heading)

            # What's the largest move we can make down this edge?
            move = self.edge_move(edge)

            return Rotation.LEFT, move

        # If it's not a node, just move forward.
        if not self.node_sensed(readings):
            # Get the edge we're currently on.
            edge = self.find_edge_from_node(self.last_node, self.heading)

            # If we're on an edge, move further if possible.
            move = self.edge_move(edge) if edge else 1

            return Rotation.NONE, move
        
        # At this point we've decided that the square is a node.

        # Add the node if it hasn't been already.
        node_already_added = self.node_added(square_id)
        if not node_already_added:
            # Add the node.
            self.add_node(square_id)

        # We're turning around on the spot, don't need to add an edge.
        if square_id != self.last_node:
            # Check if edge already exists.
            if not self.find_edge_by_nodes(self.last_node, square_id):
                # Add the new edge.
                self.add_edge(self.last_node, square_id)
            else:
                # Increment the number of traversals for this edge.
                self.increment_traversal(self.last_node, square_id)

        # Get a prob for each direction.
        sensors = np.array([])
        weights = np.array([], dtype=np.float32)
        traversals = np.array([], dtype=np.int8)
        move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for i, reading in enumerate(readings):
            # Don't consider the move if we'll hit a wall.
            if reading == 0: continue

            # Create the Sensor.
            sensor = Sensor(i)

            # Get the edge we'll be traversing if we take this move.
            sensor_heading = Heading.rotate(self.heading, Sensor.rotation(sensor))
            edge = self.find_edge_from_node(square_id, sensor_heading)

            # Get number of traversals. 0 if edge isn't recorded.
            traversal = edge['traversals'] if edge else 0

            # Don't take the edge if we've been there twice already.
            if traversal == 2:
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
            num_traversals = self.find_edge_by_nodes(self.last_node, square_id)['traversals']
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

