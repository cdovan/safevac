import networkx as nx
from networkx.algorithms.shortest_paths.weighted import single_source_dijkstra
from networkx.algorithms.flow import edmonds_karp
from math import sqrt
from copy import deepcopy

class HumanPathFinder:
	def __init__(self, nodes, exits, edges):
		self.nodes = nodes
		self.exits = exits
		self.edges = edges
		self.graph = construct_graph(self.edges)

	def shortest_paths_to_exit(self, humans):
		paths = {}

		for human, s in humans.items():
			paths[human] = self.shortest_path_to_exit(s)
		
		return paths

	def shortest_path_to_exit(self, s):
		min_distance = float("inf")
		min_path = None

		lengths, paths = single_source_dijkstra(self.graph, s, weight='weight')
		
		for e in self.exits:
			if lengths[e] < min_distance:
				min_distance = lengths[e]
				min_path = paths[e]
		
		if min_path == None:
			min_path = []
	
		return min_path
	
	def set_edge_obstacle(self, u, v):
		self.graph.edges[u, v]['weight'] = float('inf')

	def remove_edge_obstacle(self, u, v):
		self.graph.edges[v, u]['weight'] = self.graph.edges[v, u]['distance']

	def set_node_obstacle(self, v):
		for u in self.graph[v].keys():
			self.set_edge_obstacle(u, v)

	def remove_node_obstacle(self, v):
		for u in self.graph[v].keys():
			self.remove_edge_obstacle(u, v)

class RobotPathFinder:
	def __init__(self, nodes, exits, edges):
		self.nodes = nodes
		self.exits = exits
		self.edges = edges
		self.flow_graph = construct_flow_graph(self.nodes, self.edges)
		self.emergency_paths = {}

	def shortest_paths_to_safe_space(self, humans, robots):
		if len(robots) == 0:
			return {}
		
		flow_graph = deepcopy(self.flow_graph)
		
		# Paths should start at the nodes where robots are located
		for s in robots.values():
			flow_graph.add_edge('s', s + 'i', capacity=1)
		
		# Path should lead to a node that is not used by any human
		for n in self.nodes:
			is_emergency_node = False
			for ep in self.emergency_paths.values():
				if n in ep:
					is_emergency_node = True
					break

			if not is_emergency_node:
				flow_graph.add_edge(n + 'o', 't', capacity=1)
		
		# Never go to nodes where humans are located
		for n in humans.values():
			set_flow_node_obstacle(flow_graph, n)
		
		# Never go to exits
		for e in self.exits:
			set_flow_node_obstacle(flow_graph, e)

		# Calculate best flow
		residual = edmonds_karp(flow_graph, 's', 't')
		paths = {}

		# Convert residual flow into paths for every robot
		# Strip unnecessary intermediate nodes from the path that are only relevant for the flow calculation
		for robot, s in robots.items():
			flow_path = find_flow_path(residual, s + 'o', 't')
			if flow_path == None:
				paths[robot] = []
			else:
				flow_path.remove('t')

				path = []

				for fp in flow_path:
					if fp[-1] == 'o':
						path.append(fp[:-1])
				
				paths[robot] = path
		
		return paths
	
	def set_emergency_path(self, human, path):
		self.emergency_paths[human] = path

	def remove_emergency_path(self, human):
		if human in self.emergency_paths:
			del self.emergency_paths[human]
	
	def set_flow_edge_obstacle(self, u, v):
		set_flow_edge_obstacle(self.flow_graph, u, v)
	
	def remove_flow_edge_obstacle(self, u, v):
		remove_flow_edge_obstacle(self.flow_graph, u, v)
	
	def set_flow_node_obstacle(self, v):
		set_flow_node_obstacle(self.flow_graph, v)
	
	def remove_flow_node_obstacle(self, v):
		remove_flow_node_obstacle(self.flow_graph, v)

def set_flow_edge_obstacle(flow_graph, u, v):
	if (u + 'o', v + 'i') in flow_graph:
		flow_graph.remove_edge(u + 'o', v + 'i')
	
	if (v + 'o', u + 'i') in flow_graph:
		flow_graph.remove_edge(v + 'o', u + 'i')

def remove_flow_edge_obstacle(flow_graph, u, v):
	flow_graph.add_edge(u + 'o', v + 'i', capacity=1)
	flow_graph.add_edge(v + 'o', u + 'i', capacity=1)

def set_flow_node_obstacle(flow_graph, v):
	if (v + 'i', v + 'o') in flow_graph:
		flow_graph.remove_edge(v + 'i', v + 'o')

def remove_flow_node_obstacle(flow_graph, v):
	flow_graph.add_edge(v + 'i', v + 'o', capacity=1)

class Navigator:
	def __init__(self, nodes, hpf, rpf):
		self.nodes = nodes
		self.humans = {}
		self.robots = {}
		self.hpf = hpf
		self.rpf = rpf
	
	def register_human(self, human):
		self.humans[human] = { 'path': [], 'node': None }
	
	def register_robot(self, robot):
		self.robots[robot] = { 'path': [], 'node': None }
	
	def update_human_path(self, human):
		current_node = self.humans[human]['node']
		path = self.hpf.shortest_path_to_exit(current_node)
		self.humans[human]['path'] = path

		# Add new path to the emergency paths
		self.rpf.set_emergency_path(human, path)

	def update_positions(self, human_positions, robot_positions, force_path_update=False):
		any_human_path_changed = force_path_update
		human_sources = {}

		# Convert human positions into nodes
		for h, pos in human_positions.items():
			current_node = find_closest_node(self.nodes, pos)

			self.humans[h]['node'] = current_node
			human_sources[h] = current_node

			# Check whether human deviated from original path
			should_update_path = force_path_update

			if not should_update_path:
				should_update_path = self.human_off_path(h, current_node)
			
			if should_update_path:
				# If so, calculate a new path based on current location
				self.update_human_path(h)
				any_human_path_changed = True
			else:
				# Check whether end of path has been reached
				if current_node == self.humans[h]['path'][-1]:
					self.rpf.remove_emergency_path(h)
		
		any_robot_path_changed = force_path_update
		robot_sources = {}

		for r, pos in robot_positions.items():
			current_node = find_closest_node(self.nodes, pos)
			self.robots[r]['node'] = current_node
			robot_sources[r] = current_node
			path_changed = self.robot_off_path(r, current_node)
			if path_changed:
				any_robot_path_changed = True

		if any_human_path_changed or any_robot_path_changed:
			robot_paths = self.rpf.shortest_paths_to_safe_space(human_sources, robot_sources)
			for r, path in robot_paths.items():
				self.robots[r]['path'] = path

	def human_off_path(self, human, current_node):
		if human in self.humans:
			return current_node not in self.humans[human]['path']
		else:
			return True

	def robot_off_path(self, robot, current_node):
		if robot in self.robots:
			return current_node not in self.robots[robot]['path']
		else:
			return True

	def navigate_human(self, human):
		if self.humans[human]['path'] == None:
			return None

		path = self.humans[human]['path']
		current_node = self.humans[human]['node']

		if len(path) == 1:
			return None
		else:
			next_node_index = path.index(current_node) + 1
			return path[next_node_index]
	
	def navigate_robot(self, robot):
		if self.robots[robot]['path'] == None:
			return None

		path = self.robots[robot]['path']
		current_node = self.robots[robot]['node']

		if len(path) == 1:
			return None
		else:
			next_node_index = path.index(current_node) + 1
			return path[next_node_index]

def read_nodes(filename):
	f = open(filename, "r")
	nodes = {}
	exits = []

	for node_line in f:
		node_data = node_line.split(",")
		node_id = node_data[0]
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
		node1 = edge[0]
		node2 = edge[1]
		node_data1 = nodes[node1]
		node_data2 = nodes[node2]
		distance = sqrt((float(node_data1["x"]) - float(node_data2["x"]))**2 + (float(node_data1["y"]) - float(node_data2["y"]))**2)
		edges[(node1, node2)] = distance
	
	f.close()
	return edges

def find_closest_node(nodes, position):
	shortest_dist = float("inf")
	closest_node = None

	for id, node in nodes.items():
		dist = sqrt((float(node["x"]) - float(position["x"]))**2 + (float(node["y"]) - float(position["y"]))**2)
		if (dist < shortest_dist):
			shortest_dist = dist
			closest_node = id
	
	return closest_node

def construct_flow_graph(nodes, edges):
	graph = nx.DiGraph()

	for node in nodes:
		graph.add_edge(node + 'i', node + 'o', capacity=1)

	for edge in edges.keys():
		graph.add_edge(edge[0] + 'o', edge[1] + 'i', capacity=1)
		graph.add_edge(edge[1] + 'o', edge[0] + 'i', capacity=1)
	
	return graph

def construct_graph(edges):
	graph = nx.Graph()

	for edge, distance in edges.items():
		graph.add_edge(edge[0], edge[1], distance=distance, weight=distance)

	return graph

def find_flow_path(R, origin, dest):
	if origin == dest:
		return [dest]
	
	for n in R.neighbors(origin):
		if R[origin][n]['flow'] > 0:
			path = find_flow_path(R, n, dest)
			path.insert(0, origin)
			return path
	
	return None