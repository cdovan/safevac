from navigation import construct_graph, navigate_to_exit
from dijkstar import find_path

g = construct_graph("nodes.txt", "edges.txt")
s = 3
exits = [8, 16]
path = navigate_to_exit(g, s, exits)

print(path)