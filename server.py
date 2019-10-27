import socket
import sys
from time import sleep
from time import time
import navigation as nav
from location_requester import LocationRequester

ALERT = False

nodesKnown = [
    '192.168.43.184',
    '192.168.43.185'
]

commands = {
    'a'
}

nodesActive = {}

panicAddress = ('', 10000)

loc_req = LocationRequester()

map_nodes, exits = nav.read_nodes("nodes.txt")
map_edges = nav.read_edges("edges.txt", map_nodes)

human_pf = nav.HumanPathFinder(map_nodes, exits, map_edges)
robot_pf = nav.RobotPathFinder(map_nodes, exits, map_edges)
navigator = nav.Navigator(map_nodes, human_pf, robot_pf)

class type_t:
    human = 1
    arm = 2
    car = 3
    crane = 4
    detector = 5

class Node:
    def __init__(self, ip, type_t):
        self.ip = ip
        self.port = 10000
        self.address = (ip, self.port)
        self.type = type_t
        self.alarm = False

def updateConnections():
    for n in nodesKnown:
        if n in nodesActive.keys():
            continue
            
        try:
            server_address = (n, 10001)
            print('Connecting to %s port %s' % server_address)
            newSocket.connect(server_address)
            print('Connection Successful, sending init')
            newSocket.sendall(b'CONNINIT')

            msg = newSocket.recv(16)
            print('received "%s"' % msg)

            data = str(msg)[2:-1].split('_')

            if data[0] == 'CONNACK':
                tagid = int(data[1])
                is_human = int(data[2]) == 1
            
                loc_req.register_device(tagid)

                if is_human:
                    navigator.register_human(tagid)
                else:
                    navigator.register_robot(tagid)

                nodesActive[n] = (newSocket, tagid, is_human)

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

def update_positions():
    locations = loc_req.request_locations()
    humans = {}
    robots = {}

    for data in nodesActive.values():
        tagid = data[1]
        is_human = data[2]
        if is_human:
            humans[tagid] = locations[tagid]
        else:
            robots[tagid] = locations[tagid]

    navigator.update_positions(humans, robots)

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
    
    update_positions()

    lost_nodes = []

    for ip,data in nodesActive.items():
        node_socket = data[0]
        tagid = data[1]
        is_human = data[2]

        try:
            # navigation update
            map_node = None

            if is_human:
                map_node = navigator.navigate_human(tagid)
            else:
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

            if reply == b'PANICINIT':
                print('%s: Alert recieved' % ip)
                ALERT = True
                panicAddress = ip
            elif reply == b'PANIC':
                print('%s: Continuing panic' % ip)
            elif reply == b'OK':
                print('%s: OK' % ip)
            else:
                print('Unknown message received from node! Continuing...')
        except:
            print('Node connection is broken!')
            node_socket.close()
            lost_nodes.append(ip)
    
    for ip in lost_nodes:
        del nodesActive[ip]
    
    msg = ''

def cmdThread():
    while True:
        print('SAFEVAC Server Console')
        cmd = raw_input('$ ')
        if cmd not in commands:
            print('Invalid input')