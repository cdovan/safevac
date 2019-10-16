from dijkstar import Graph, find_path
from math import sqrt

def navigate_to_exit(graph, s, exits):
	min_cost = float("inf")
	min_path = None

	cost_func = lambda u, v, e, prev_e: e['cost']
	for e in exits:
		path = find_path(graph, s, e, cost_func=cost_func)
		path_cost = path.total_cost

		if path_cost < min_cost:
			min_cost = path_cost
			min_path = path
	
	return min_path

def construct_graph(nodes_filename, edges_filename):
	nodes_file = open(nodes_filename, "r")
	edges_file = open(edges_filename, "r")

	nodes = {}

	for node_data in nodes_file:
		node = node_data.split(",")
		nodes[int(node[0])] = { "x": float(node[1]), "y": float(node[2]) }

	graph = Graph()

	for edge_data in edges_file:
		edge = edge_data.strip("\n").split(",")
		node1 = int(edge[0])
		node2 = int(edge[1])
		node_data1 = nodes[node1]
		node_data2 = nodes[node2]
		distance = sqrt((node_data1["x"] - node_data2["x"])**2 + (node_data1["y"] - node_data2["y"])**2)
		graph.add_edge(node1, node2, { "cost": distance})
		graph.add_edge(node2, node1, { "cost": distance})

	nodes_file.close()
	edges_file.close()

	return graph