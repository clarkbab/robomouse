import pdb
import math
import numpy as np
from mice.mixins import StateMixin
from heading import Heading
from rotation import Rotation
from sensor import Sensor

class AStarMouse(StateMixin):
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

    def heuristic_cost(self, start_node, end_node):
        # Get start and end node positions.
        start_pos, end_pos = self.square_position(start_node), self.square_position(end_node)

        # Calculate the min steps required in each direction.
        diff = np.abs(end_pos - start_pos)
        x_min = math.ceil(diff[0] / self.MAX_MOVE)
        y_min = math.ceil(diff[1] / self.MAX_MOVE) 

        # Return the sum of moves.
        return x_min + y_min

    def ancestral_path(self, node, ancestors):
        # Keep track of ancestors.
        path = np.array([], dtype=np.int8)

        # Set starting condition.
        current_node = node
        path = np.append(path, current_node)

        # Loop until we're out of ancestors.
        while current_node in ancestors:
            # Load the next ancestor.
            current_node = ancestors[current_node]

            # Add ancestor to the path.
            path = np.append(path, current_node)

        # Reverse the path list and return.
        return np.flip(path)

    def shortest_path(self, start_node, end_node):
        """Calculate the shortest path from start to end node.
        """
        # Create a priority queue to process nodes.
        queue = np.array([], dtype=np.int8)

        # Track evaluated nodes.
        evaluated = np.array([], dtype=np.int8)

        # Store g-scores for each node. We need this to calculate g-score for
        # new nodes.
        g_scores = dict()

        # Store f_scores for each node, this will be used to sort the priority
        # queue.
        f_scores = dict()

        # Add the start node info.
        queue = np.append(queue, start_node)
        g_scores[start_node] = 0
        h_score = self.heuristic_cost(start_node, end_node)
        f_scores[start_node] = h_score

        # Keep track of each ancestor for a particular node. We'll use this to
        # build our path later.
        ancestors = dict()

        # Process nodes and re-order priority queue.
        while len(queue) != 0:
            # Pull first node off priority queue.
            node, queue = queue[0], queue[1:] 

            # If node is goal, break from the loop.
            if node == end_node:
                path = self.ancestral_path(node, ancestors)
                return path

            # Find edges and connected nodes.
            edges = self.nodes[node]

            # For each node.
            for edge in edges:
                # Get new node.
                new_node = edge['node']

                # Ignore node if we've already evaluated it.
                if new_node in evaluated:
                    continue

                # Get the edge length. Crucially, this will be the minimum
                # number of moves the mouse can take to traverse the edge, not
                # the length in squares.
                d_score = math.ceil(edge['length'] / self.MAX_MOVE)

                # Calculate the next node's g-score.
                g_score = g_scores[node] + d_score

                # Have we already reached this node via another ancestor?
                if new_node in g_scores:
                    # Is the other path shorter or the same?
                    if g_score >= g_scores[new_node]:
                        continue

                # Add/update the ancestor node.
                ancestors[new_node] = node

                # Find the heuristic distance to the goal.
                h_score = self.heuristic_cost(edge['node'], end_node)

                # F-score is the sum of g-score and h-score.
                f_score = g_score + h_score

                # Add/update the g-score and f-score.
                g_scores[new_node] = g_score
                f_scores[new_node] = f_score

                # Add the new node to the priority queue.
                queue = np.append(queue, new_node)

                # Sort the priority queue by f-score.
                sort_func = lambda node: f_scores[node]
                queue = np.array(sorted(queue, key=sort_func))
            
            # Mark node as evaluated.
            evaluated = np.append(evaluated, node)

        # Never reached the goal node.
        return None

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
            print(f"[MOUSE] run: {self.run}")
            print(f"[MOUSE] pos: {self.pos}")
            print(f"[MOUSE] heading: {self.heading}")

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
        # Get sensors leading to exits.
        exits = np.nonzero(readings)[0]

        # If sensor readings are all blank, we're at a node.
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

        # If we're executing, follow the path.
        if self.run == self.EXEC_RUN:
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
            edge = self.find_edge_by_nodes(self.last_node, node)

            # Compare the current heading to desired heading.
            rot = None
            for rotation in Rotation:
                if Heading.rotate(self.heading, rotation) == edge['heading']:
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
            self.add_node(square_id)
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

        # Check if we should reset.
        if self.reached_goal:
            if self.verbose: print(f"[MOUSE] Finished planning.")

            # Get the start and end nodes.
            start_node = self.square_id(self.init_state['pos'])
            end_node = square_id

            # Find the shortest path from start to finish. Remove first node as
            # we're starting there.
            self.path = self.shortest_path(start_node, end_node)

            # Begin execution phase.
            self.start_execution()
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

