import numpy as np
from heading import Heading

class Graph:
    MAX_MOVE = 3

    def __init__(self):
        # Initialise the nodes dictionary.
        self.nodes = dict()

    def add_node(self, node):
        """Adds a new node.

        Arguments:
            node -- a unique ID for the node.
        """
        # Record the node.
        self.nodes[node] = np.array([])

    def add_edge(self, node1, node2, dist, heading):
        """Adds a new edge.

        Arguments:
            node1 -- the unique ID of the first node on the edge.
            node2 -- the unique ID of the second node on the edge.
            dist -- the distance in squares between nodes.
            heading -- the heading from first node to second node.
        """
        # Get opposite heading.
        opp_heading = heading.opposite()

        # Add connections.
        edge1 = { 'node': node2, 'length': dist, 'heading': heading, 'traversals': 1 }
        edge2 = { 'node': node1, 'length': dist, 'heading': opp_heading, 'traversals': 1 }
        self.nodes[node1] = np.append(self.nodes[node1], edge1)
        self.nodes[node2] = np.append(self.nodes[node2], edge2)

    def find_edge_by_nodes(self, node1, node2):
        """Gets the edge between two nodes.
        """
        return next((e for e in self.nodes[node1] if e['node'] == node2), None)

    def find_edge_by_heading(self, node, heading):
        """Gets an edge radiating out from a node.
        """
        return next((e for e in self.nodes[node] if e['heading'] == heading), None)


    def increment_traversal(self, node1, node2):
        # Load the edges.
        edge1 = self.find_edge_by_nodes(node1, node2)
        edge2 = self.find_edge_by_nodes(node2, node1)

        # Increment the traversals.
        edge1['traversals'] += 1
        edge2['traversals'] += 1

    def node_added(self, node):
        """Checks if a node is present in the graph.

        Arguments:
            node -- the unique ID of the node.
        """
        return node in self.nodes

    def shortest_path(self, start_node, end_node, heuristic):
        """Calculates the shortest path between nodes using the A* algorithm.

        Arguments:
            start_node -- the unique ID of the start node.
            end_node -- the unique ID of the end node.
            heuristic -- a function with signature (node1, node2) that returns
                the loss between a start and destination node.
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
        h_score = heuristic(start_node, end_node)
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
                path = self.__ancestral_path(node, ancestors)
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
                d_score = np.ceil(edge['length'] / self.MAX_MOVE)

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
                h_score = heuristic(edge['node'], end_node)

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

    def __ancestral_path(self, node, ancestors):
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

