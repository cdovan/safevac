import socket
import sys
from pyping import ping
from time import sleep

ALERT = False

nodesKnown = [
    '192.168.43.184',
    '192.168.43.185'
]

nodesActive = [None] * len(nodes)

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

sockets = [None] * len(nodesKnown)

def updateConnections():
    for i in range(len(nodesKnown)):
        if not ping(nodesKnown[i]):
            continue
        try:
            nodesActive.append(nodesKnown[i])
            newSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            newSocket.settimeout(2)

            server_address = (nodesKnown[i], 10000)
            newSocket.connect(server_address)
            print ('connecting to %s port %s' % server_address)

            msg = newSocket.recv(16)
            if msg != 'CONN_ACK':
                print('Node has not acknowledged new connection! Continuing...')
            sockets.append(newSocket)
        except:
            print('[SEVERE] Socket connection failed unexpectedly! Socket list may be corrupted!')

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

updateConnections()

# Main Loop
while True:
    for i in range(len(nodesActive)):

        # Send command to node
        if ALERT and nodesActive[i] != panicAddress:
            sock[i].sendall('PANIC_EXTERN')
        if ALERT and nodesActive[i] == panicAddress:
            sock[i].sendall('PANIC_CONT')
        else:
            sock[i].sendall('DATA_REQ')

        # Receive and respond to node
        msg = sock[i].recv(16)
        print('received "%s"' % msg)

        if msg == 'PANIC':
            ALERT = True
            panicAddress = nodesActive[i]
            print(nodesActive[i], ': Alert recieved')
        elif msg == 'OK':
            print(nodesActive[i], ': OK')
        else:
            print('Unknown message received from node! Continuing...')
    
    sleep(1)
