import socket
import sys
from time import sleep

ALERT = False

nodes = [
    '192.168.43.184'
]

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

sock = [None] * 10

# Establish sockets for each node
for i in range(len(nodes)):
    sock[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock[i].settimeout(10)

# Connect to nodes
print('Connecting to all known nodes')
for i in range(len(nodes)):
    server_address = (nodes[i], 10000)
    print ('connecting to %s port %s' % server_address)
    sock[i].connect(server_address)
    sock[i].sendall('CONN_INIT')
    msg = sock[i].recv(16)
    if msg != 'CONN_ACK':
        print('Node has not acknowledged new connection! Continuing...')

# Main Loop
while True:
    for i in range(len(nodes)):

        # Send command to node
        if ALERT and nodes[i] != panicAddress:
            sock[i].sendall('PANIC_EXTERN')
        if ALERT and nodes[i] == panicAddress:
            sock[i].sendall('PANIC_CONT')
        else:
            sock[i].sendall('DATA_REQ')

        # Receive and respond to node
        msg = sock[i].recv(16)
        print('received "%s"' % msg)

        if msg == 'PANIC':
            ALERT = True
            panicAddress = nodes[i]
            print(nodes[i], ': Alert recieved')
        elif msg == 'OK':
            print(nodes[i], ': OK')
        else:
            print('Unknown message received from node! Continuing...')
    
    sleep(1)
