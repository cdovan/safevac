import socket
import sys
from pyping import ping
from time import sleep
from time import time

ALERT = True

nodesKnown = [
    '192.168.43.184',
    '192.168.43.185'
]

commands = {
    'a'
}

nodesActive = []

panicAddress = ('', 10000)

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

sockets = []

def updateConnections():
    for i in range(len(nodesKnown)):
        if nodesKnown[i] in nodesActive:
            continue
            
        try:
            newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newSocket.settimeout(0.5)

            server_address = (nodesKnown[i], 10000)
            print ('connecting to %s port %s' % server_address)
            newSocket.connect(server_address)
            newSocket.sendall('CONN_INIT')

            msg = newSocket.recv(16)
            if msg != 'CONN_ACK':
                print('Node has not acknowledged new connection! Continuing...')

            sockets.append(newSocket)
            nodesActive.append(nodesKnown[i])
        
        except:
            print('Unable to connect to node')
            if nodesKnown[i] in nodesActive:
                nodesActive.remove(nodesKnown[i])
    if (len(nodesActive) == 0):
        print('Unable to connect to any known nodes, retrying in 5 seconds...')

'''

# Establish sockets for each node
for i in range(len(nodes)):
    sock[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock[i].settimeout(10)

# Connect to nodes
print('Connecting to all known nodes')
j = 0
for i in range(len(nodesKnown)):
    server_address = (nodesKnown[i], 10000)
    print ('connecting to %s port %s' % server_address)

    try:
        sock[i].connect(server_address)
        sock[i].sendall('CONN_INIT')
        msg = sock[i].recv(16)
        nodesActive[j] = nodesKnown[i]
        if msg != 'CONN_ACK':
            print('Node has not acknowledged new connection! Continuing...')

    except:
        print('Could not reach %s', nodes[i])
    
    j += 1
'''
cmd = ''

lastUpdate = time()
updateConnections()
panicAddress = ''

# Main Loop
while True:
    if time() - lastUpdate > 5:
        print('Updating list of active nodes')
        lastUpdate = time()
        updateConnections()

    for i in range(len(sockets)):
        if sockets[i] == None:
            continue

        # Send command to node
        if ALERT and nodesActive[i] != panicAddress:
            msg = 'PANIC_EXTERN'
        if ALERT and nodesActive[i] == panicAddress:
            msg = 'PANIC_CONT'
        else:
            msg = 'DATA_REQ'
        
        print('Sending "%s"' % msg)
        sockets[i].sendall(msg)

        # Receive and respond to node
        msg = sockets[i].recv(16)
        print('received "%s"' % msg)

        if msg == 'PANIC_INIT':
            print('%s: Alert recieved' % nodesActive[i])
            ALERT = True
            panicAddress = nodesActive[i]
        elif msg == 'PANIC':
            print('%s: Continuing panic' % nodesActive[i])
        elif msg == 'OK':
            print('%s: OK' % nodesActive[i])
        else:
            print('Unknown message received from node! Continuing...')
    
    sleep(1)

def cmdThread():
    while True:
        print('SAFEVAC Server Console')
        cmd = raw_input('$ ')
        if cmd not in commands:
            print('Invalid input')