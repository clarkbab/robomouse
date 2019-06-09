import pdb
import numpy as np
from mice.mixins import StateMixin

class TremauxMouse(StateMixin):
    MAX_MOVE = 3

    def __init__(self, maze_dim, init_state, verbose):
        super().init(maze_dim, init_state, verbose)
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

    def next_move(self, sensors):
        # Print mouse's assumed location.
        if self.verbose:
            print(f"[MOUSE] run: {self.run}")
            print(f"[MOUSE] pos: {self.pos}")
            print(f"[MOUSE] heading: {self.heading}")

        # Updates mouse's state.
        rot, move = self.make_move(sensors)

        # check if we're in the goal.
        if self.in_goal():
            self.reached_goal = True
            if self.verbose:
                print(f"[MOUSE] reached goal.")

            if self.run == self.EXEC_RUN:
                if self.verbose: print(f"[MOUSE] finished.")

        return rot, move

    def square_position(self, square_id):
        """Gets the position of a square.
        """
        # Get x, y coordinates.
        x = square_id % self.maze_dim
        y = int(square_id / self.maze_dim)

        return np.array([x, y])

    def find_edge(self, node1, node2):
        return next((e for e in self.nodes[node1] if e['node'] == node2), None)

    def add_edge(self, node1, node2):
        # Get positions of nodes.
        node_pos1 = self.square_position(node1)
        node_pos2 = self.square_position(node2)

        # Get distance between nodes.
        vec = node_pos2 - node_pos1
        dist = int(np.linalg.norm(vec))

        # Get headings traversing from node 1 to 2, and reverse.
        head_vect = vec / dist 
        heading1 = next(k for k, v in self.HEADING_COMPONENTS_MAP.items() if np.array_equal(head_vect, v))
        heading2 = self.new_heading(heading1, 180)

        # Add connections.
        edge1 = { 'node': node2, 'length': dist, 'heading': heading1, 'traversals': 1 }
        edge2 = { 'node': node1, 'length': dist, 'heading': heading2, 'traversals': 1 }
        self.nodes[node1] = np.append(self.nodes[node1], edge1)
        self.nodes[node2] = np.append(self.nodes[node2], edge2)

    def increment_traversal(self, node1, node2):
        # Load the edges.
        edge1 = self.find_edge(node1, node2)
        edge2 = self.find_edge(node2, node1)

        # Increment the traversals.
        edge1['traversals'] += 1
        edge2['traversals'] += 1

    def node_added(self, node):
        return node in self.nodes

    def node_sensed(self, sensors):
        """
        Looks like a node if the left or right sensor-readings are non-zero, or
        we're at a dead-end and all readings are zero.

        Makes assumptions that there is an exit behind us.
        """
        # Get sensors leading to exits.
        exits = np.nonzero(sensors)[0]

        # If sensor readings are all blank, we're at a node.
        if len(exits) == 0:
            return True

        # If left or right passages are exits, we're at a node. This is because,
        # assuming there is a passage behind us, there is an l-bend at this
        # square.
        if 0 in exits or 2 in exits:
            return True

        return False

    def add_node(self, node):
        # Record the node.
        self.nodes[node] = np.array([])

    def get_edge(self, node, heading):
        return next((e for e in self.nodes[node] if e['heading'] == heading), None)

    def is_node(self, readings):
        """
        If it has an l-bend or it's a dead-end, it's a node.
        """
        # Get all exits.
        exits = np.nonzero(readings)[0]

        # Check if it's a dead-end.
        if len(exits) == 1:
            return True

        # Compare adjacent pairs of readings.
        for r1, r2 in zip(readings, np.roll(readings, 1)):
            if r1 != 0 and r2 != 0:
                return True

        return False

    def initial_node_sensed(self, sensors):
        """Checks if we're at a node initially.

        In normal operation, we know that we came from a path behind us and we
        use the existence of this exit to say whether we're at a node.
        """
        # Get sensors leading to exits.
        exits = np.where(sensors != 0)[0]

        # If sensors are all black, we're at a node.
        if len(exits) == 0:
            return True

        # Look for an l-bend at this square.
        if len(exits) > 1 and 1 in exits:
            return True

        return False

    def make_move(self, sensors):
        # Get the ID of the current square.
        square_id = self.square_id(self.pos)

        # If it's our first move, mark the square as a node and pick an exit or
        # rotate.
        if self.initialising:
            self.initialising = False
            self.add_node(square_id)
            self.last_node = square_id

            # Get all the exits.
            exits = np.nonzero(sensors)[0]

            # If no exits, rotate.
            if len(exits) == 0:
                self.update_state(-90, 0)
                return -90, 0

            # Pick the first exit.
            rot = self.SENSOR_ROTATION_MAP[exits[0]]
            self.update_state(rot, 1)
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
            self.update_state(-90, 1)
            return -90, 1

        # If it's not a node, just move forward.
        if not self.node_sensed(sensors):
            # Are we on an edge?
            # Are there any recorded edges that run from the last node in our
            # current heading?
            edge = next((e for e in self.nodes[self.last_node] if e['heading'] == self.heading), None)

            # If the edge exists, use this info to take the largest step we can.
            if edge:
                # What's the largest step we can take.
                next_node_pos = self.square_position(edge['node'])
                max_move_vec = next_node_pos - self.pos
                move = int(min(np.linalg.norm(max_move_vec), self.MAX_MOVE))
                self.update_state(0, move)
                return 0, move
            
            self.update_state(0, 1)
            return 0, 1
        
        # At this point we've decided that the square is a node.

        # Add the node if it hasn't been already.
        node_already_added = self.node_added(square_id)
        if not node_already_added:
            # Add the node.
            self.add_node(square_id)

        # We're turning around on the spot, don't need to add an edge.
        if square_id != self.last_node:
            # Check if edge already exists.
            if not self.find_edge(self.last_node, square_id):
                # Add the new edge.
                self.add_edge(self.last_node, square_id)
            else:
                # Increment the number of traversals for this edge.
                self.increment_traversal(self.last_node, square_id)

        # Get a prob for each direction.
        sensor_ids = np.array([], dtype=np.int8)
        weights = np.array([], dtype=np.float32)
        traversals = np.array([], dtype=np.int8)
        move_vecs = np.ndarray((0, 2), dtype=np.int8)
        for i, reading in enumerate(sensors):
            # Don't consider the move if we'll hit a wall.
            if reading == 0: continue

            # Get the edge we'd be traversing, if it's marked.
            sensor_heading = self.new_heading(self.heading, self.SENSOR_ROTATION_MAP[i])
            edge = self.get_edge(square_id, sensor_heading)

            # Get number of traversals.
            traversal = edge['traversals'] if edge else 0

            # Don't take the edge if we've been there twice already.
            if traversal == 2:
                continue

            # Get the move vector components.
            move_vec = self.HEADING_COMPONENTS_MAP[sensor_heading]
            
            # Add the number of edge traversals.
            traversals = np.append(traversals, traversal)

            # Add the move vec and sensor ID.
            move_vecs = np.vstack((move_vecs, move_vec))
            sensor_ids = np.append(sensor_ids, i)

            # How much of this move is towards the centre?
            weight = np.dot(move_vec, self.unit_centre())
            weights = np.append(weights, weight)

        # If no possible moves, let's turn around.
        if len(move_vecs) == 0:
            self.last_node = square_id
            self.update_state(-90, 0)
            return -90, 0

        # If we're not turning on the spot, and we've already seen the node.
        if self.last_node != square_id and node_already_added:
            # If we only traversed the last edge once, go back that way. We've
            # reached the end of a branch in our depth-first search algorithm.
            num_traversals = self.find_edge(self.last_node, square_id)['traversals']
            if num_traversals == 1:
                self.last_node = square_id
                self.backtrack = True
                self.update_state(-90, 0)
                return -90, 0

        # Take the road less travelled, i.e, select those squares that we've visited less.
        min_idx = np.argwhere(traversals == np.min(traversals)).flatten()

        # Only keep edges with minimum traversals.
        sensor_ids = sensor_ids[min_idx]
        weights = weights[min_idx]
        move_vecs = move_vecs[min_idx]

        # Apply the softmax function.
        probs = self.softmax(weights)
        
        # Get a sensor based on the probs.
        sensor_id = np.random.choice(sensor_ids, p=probs)
        idx = np.where(sensor_ids == sensor_id)[0][0]

        # Get the rotation and move to perform.
        rot = self.SENSOR_ROTATION_MAP[sensor_id]
        move_vec = move_vecs[idx]
        move = abs(move_vec).max()
        
        # Update internal state.
        self.update_state(rot, move)
        self.last_node = square_id
        
        # The last thing we do is update our state. We don't know anything about
        # the next square at this point; this info will be handed to us with the
        # next sensor reading. So it doesn't make any sense to start working on
        # adding the next node or anything. In fact, we don't know if this step
        # will bring us to a node or a passage until we get sensor readings.

        return rot, move

