import socket
import sys
from time import sleep
from time import time
import navigation as nav
from location_requester import LocationRequester
import device_types

ALERT = False
PORT = 10000

nodesKnown = [
    '192.168.43.184',
    '192.168.43.185'
]

nodesActive = {}
panicAddress = ('', 10000)

loc_req = LocationRequester()

map_nodes, exits = nav.read_nodes("nodes.txt")
map_edges = nav.read_edges("edges.txt", map_nodes)

human_pf = nav.HumanPathFinder(map_nodes, exits, map_edges)
robot_pf = nav.RobotPathFinder(map_nodes, exits, map_edges)
navigator = nav.Navigator(map_nodes, human_pf, robot_pf)
force_path_update = False
pending_dangers = []

def updateConnections():
    for n in nodesKnown:
        if n in nodesActive.keys():
            continue
            
        try:
            newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newSocket.settimeout(3)
            server_address = (n, 10000)
            print('Connecting to %s port %s' % server_address)
            newSocket.connect(server_address)
            print('Connection Successful, sending init')
            newSocket.sendall(b'CONNINIT')

            msg = newSocket.recv(16)
            print('received "%s"' % msg)

            data = str(msg)[2:-1].split('_')

            if data[0] == 'CONNACK':
                tagid = int(data[1])
                node_type = int(data[2])
            
                loc_req.register_device(tagid)

                if node_type == device_types.HUMAN:
                    navigator.register_human(tagid)
                elif node_type != device_types.DETECTOR:
                    navigator.register_robot(tagid)

                nodesActive[n] = (newSocket, tagid, node_type)

                print('Node has acknowledged init')
            else:
                print('Node has not acknowledged new connection! Continuing...')
        except:
            print('Unable to connect to node')

    if (len(nodesActive) == 0):
        print('Unable to connect to any known nodes, retrying in 5 seconds...')

cmd = ''
msg = b''

lastUpdate = time()
updateConnections()
panicAddress = ''

def update_positions(locations):
    humans = {}
    robots = {}

    for data in nodesActive.values():
        tagid = data[1]
        node_type = data[2]
        if node_type == device_types.HUMAN:
            humans[tagid] = locations[tagid]
        elif node_type != device_types.DETECTOR:
            robots[tagid] = locations[tagid]

    global force_path_update
    navigator.update_positions(humans, robots, force_path_update)
    force_path_update = False

def mark_safety(pos):
    if pos in pending_dangers:
        pending_dangers.remove(pos)

    human_pf.remove_node_obstacle(pos)
    robot_pf.remove_flow_node_obstacle(pos)

    global force_path_update
    force_path_update = True

def mark_danger(pos):
    pending_dangers.append(pos)

def update_dangers():
    applied_obstructions = []

    for n in pending_dangers:
        can_obstruct = True
        # Checks whether any humans are on the 
        # If so, obstruction is prevented so human can escape
        for h in navigator.humans:
            if h['node'] == n:
                can_obstruct = False
                break
        
        if can_obstruct:
            human_pf.set_node_obstacle(n)
            robot_pf.set_flow_node_obstacle(n)

            global force_path_update
            force_path_update = True
            applied_obstructions.append(n)
    
    for n in applied_obstructions:
        pending_dangers.remove(n)

def get_node_position(locations, tag_id, node_type):
    pos = None
    if node_type == device_types.DETECTOR:
        pos = nav.find_closest_node(map_nodes, locations[tagid])
    elif node_type == device_types.HUMAN:
        pos = navigator.humans[tagid]['node']
    else:
        pos = navigator.robots[tagid]['node']
    return pos

# Main Loop
while True:
    if time() - lastUpdate > 5:
        print('Updating list of active nodes')
        lastUpdate = time()
        updateConnections()
    
    print('Keyboard Interrupt to Stop Alert, one second')
    tmp = time()
    try:
        while time() - tmp < 1:
            None
    except KeyboardInterrupt:
        ALERT = False
        msg = b'PANICOFF'
    
    update_dangers()

    locations = loc_req.request_locations()
    update_positions(locations)

    lost_nodes = []

    for ip,data in nodesActive.items():
        node_socket = data[0]
        tagid = data[1]
        node_type = data[2]

        try:
            # navigation update
            map_node = None

            if node_type == device_types.HUMAN:
                map_node = navigator.navigate_human(tagid)
            elif node_type != device_types.DETECTOR:
                map_node = navigator.navigate_robot(tagid)
            
            if map_node == None:
                map_node = ''
            
            # Send command to node
            if ALERT and ip != panicAddress:
                msg = ('PANICEXTERN_%s' % map_node).encode()
            elif ALERT and ip == panicAddress:
                msg = ('PANICCONT_%s' % map_node).encode()
            elif msg != b'PANICOFF':
                msg = b'DATAREQ'

            print('Sending "%s"' % msg)
            node_socket.sendall(msg)

            # Receive and respond to node
            reply = node_socket.recv(16)
            print('received "%s"' % reply)

            reply_data = str(reply)[2:-1].split('_')

            if reply_data[0] == 'PANICINIT':
                print('%s: Alert recieved' % ip)
                ALERT = True
                panicAddress = ip
                if node_type == device_types.DETECTOR:
                    pos = get_node_position(locations, tagid, node_type)
                    mark_danger(pos)
                    print('%s: Detector alert, dangerous place marked' % ip)
            elif reply_data[0] == 'PANIC':
                print('%s: Continuing panic' % ip)
            elif reply_data[0] == 'DANGERPLACE':
                pos = get_node_position(locations, tagid, node_type)
                if pos != None:
                    mark_danger(pos)
                
                print('%s: Dangerous place marker received' % ip)
            elif reply_data[0] == 'SAFEPLACE':
                pos = get_node_position(locations, tagid, node_type)
                if pos != None:
                    mark_safety(pos)
                
                print('%s: Safe place marker received' % ip)
            elif reply_data[0] == 'OK':
                print('%s: OK' % ip)
            else:
                print('Unknown message received from node! Continuing...')
        except:
            print('Node connection is broken!')
            node_socket.close()
            lost_nodes.append(ip)
    
    for ip in lost_nodes:
        del nodesActive[ip]
    
    msg = b''