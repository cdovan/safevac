import navigation

nodes = navigation.read_nodes("nodes.txt")
edges = navigation.read_edges("edges.txt", nodes)

graph = navigation.construct_graph(edges)

navigation.set_obstacle(graph, 8)

s = 3
exits = [8, 16]
path = navigation.path_to_exit(graph, s, exits)

print(path)