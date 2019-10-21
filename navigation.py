from dijkstar import Graph, find_path
from math import sqrt

class ConstructionSite:
	def __init__(self, nodes_filename, edges_filename):
		self.nodes, self.exits = read_nodes(nodes_filename)
		self.edges = read_edges(edges_filename, self.nodes)
		self.graph = construct_graph(self.edges)

	def shortest_path_to_exit(self, s):
		min_cost = float("inf")
		min_path = None

		cost_func = lambda u, v, e, prev_e: e['cost']
		for e in self.exits:
			path = find_path(self.graph, s, e, cost_func=cost_func)
			
			if path.total_cost < min_cost:
				min_cost = path.total_cost
				min_path = path
		
		return min_path

	def set_edge_obstacle(self, u, v):
		self.graph.add_edge(u, v, { "cost": float("inf") })
		self.graph.add_edge(v, u, { "cost": float("inf") })

	def remove_edge_obstacle(self, u, v):
		if (v, u) in self.edges:
			distance = self.edges[(v, u)]
		elif (u, v) in self.edges:
			distance = self.edges[(u, v)]
		else:
			raise Exception("Neither edge " + str((v, u)) + " nor edge " + str((u, v)) + " can be found in given edges.")
		
		self.graph.add_edge(v, u, { "cost": distance })
		self.graph.add_edge(u, v, { "cost": distance })

	def set_node_obstacle(self, v):
		for u in self.graph.get_incoming(v):
			self.set_edge_obstacle(u, v)

	def remove_node_obstacle(self, v):
		for u in self.graph.get_incoming(v):
			self.remove_edge_obstacle(u, v)

def read_nodes(filename):
	f = open(filename, "r")
	nodes = {}
	exits = []

	for node_line in f:
		node_data = node_line.split(",")
		node_id = int(node_data[0])
		node_x = float(node_data[1])
		node_y = float(node_data[2])
		is_exit = int(node_data[3]) == 1

		nodes[node_id] = { "x": node_x, "y": node_y }
		
		if is_exit:
			exits.append(node_id)
	
	f.close()
	return nodes, exits

def read_edges(filename, nodes):
	f = open(filename, "r")
	edges = {}

	for edge_line in f:
		edge = edge_line.strip("\n").split(",")
		node1 = int(edge[0])
		node2 = int(edge[1])
		node_data1 = nodes[node1]
		node_data2 = nodes[node2]
		distance = sqrt((node_data1["x"] - node_data2["x"])**2 + (node_data1["y"] - node_data2["y"])**2)
		edges[(node1, node2)] = distance
	
	f.close()
	return edges

def construct_graph(edges):
	graph = Graph()

	for edge, distance in edges.items():
		graph.add_edge(edge[0], edge[1], { "cost": distance })
		graph.add_edge(edge[1], edge[0], { "cost": distance })

	return graph