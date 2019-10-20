from dijkstar import Graph, find_path
from math import sqrt
from copy import deepcopy

def path_to_exit(graph, s, exits):
	min_cost = float("inf")
	min_path = None

	cost_func = lambda u, v, e, prev_e: e['cost']
	for e in exits:
		path = find_path(graph, s, e, cost_func=cost_func)
		
		if path.total_cost < min_cost:
			min_cost = path.total_cost
			min_path = path
	
	return min_path

def set_obstacle(graph, v):
	for u in graph.get_incoming(v):
		graph.add_edge(v, u, { "cost": float("inf") })
		graph.add_edge(u, v, { "cost": float("inf") })

def remove_obstacle(graph, edges, v):
	for u in graph.get_incoming(v):
		distance = 0

		if (v, u) in edges:
			distance = edges[(v, u)]
		elif (u, v) in edges:
			distance = edges[(u, v)]
		
		graph.add_edge(v, u, { "cost": distance })
		graph.add_edge(u, v, { "cost": distance })

def read_nodes(filename):
	f = open(filename, "r")
	nodes = {}

	for node_data in f:
		node = node_data.split(",")
		nodes[int(node[0])] = { "x": float(node[1]), "y": float(node[2]) }
	
	f.close()
	return nodes

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