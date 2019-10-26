from navigation import RobotPathFinder, HumanPathFinder, Navigator
import navigation as nav

nodes, exits = nav.read_nodes("nodes.txt")
edges = nav.read_edges("edges.txt", nodes)

rpf = RobotPathFinder(nodes, exits, edges)
hpf = HumanPathFinder(nodes, exits, edges)
navigator = Navigator(nodes, hpf, rpf)

for i in range(3):
	navigator.register_human(i)

for i in range(2):
	navigator.register_robot(i)

navigator.update_positions(	{	0: { 'x': 4, 'y': 19 },
								1: { 'x': 13, 'y': 12 },
								2: { 'x': 5.5, 'y': 7.32 }
							},
							{
								0: { 'x': 1, 'y': 12 },
								1: { 'x': 0, 'y': 16 },
							})

for k,v in navigator.humans.items():
	print(str(k),":", v)

for k,v in navigator.robots.items():
	print(str(k),":", v)

next_node = navigator.navigate_human(1)

print(next_node)