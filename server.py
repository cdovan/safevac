import socket
import sys
from time import sleep
from time import time

ALERT = False

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
            newSocket.settimeout(3)

            server_address = (nodesKnown[i], 10001)
            print('Connecting to %s port %s' % server_address)
            newSocket.connect(server_address)
            print('Connection Successful, sending init')
            newSocket.sendall(b'CONN_INIT')

            msg = newSocket.recv(16)
            print('received "%s"' % msg)

            if msg == b'CONN_ACK':
                print('Node has acknowledged init')
            else:
                print('Node has not acknowledged new connection! Continuing...')

            sockets.append(newSocket)
            nodesActive.append(nodesKnown[i])
        
        except:
            print('Unable to connect to node')

    if (len(nodesActive) == 0):
        print('Unable to connect to any known nodes, retrying in 5 seconds...')

cmd = ''
msg = b''

lastUpdate = time()
updateConnections()
panicAddress = ''

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
        msg = b'PANIC_OFF'

    for i in range(len(sockets)):
        try:
            if sockets[i] == None:
                continue
            # Send command to node
            if ALERT and nodesActive[i] != panicAddress:
                msg = b'PANIC_EXTERN'
            elif ALERT and nodesActive[i] == panicAddress:
                msg = b'PANIC_CONT'
            elif msg != b'PANIC_OFF':
                msg = b'DATA_REQ'

            print('Sending "%s"' % msg)
            sockets[i].sendall(msg)

            # Receive and respond to node
            reply = sockets[i].recv(16)
            print('received "%s"' % reply)

            if reply == b'PANIC_INIT':
                print('%s: Alert recieved' % nodesActive[i])
                ALERT = True
                panicAddress = nodesActive[i]
            elif reply == b'PANIC':
                print('%s: Continuing panic' % nodesActive[i])
            elif reply == b'OK':
                print('%s: OK' % nodesActive[i])
            else:
                print('Unknown message received from node! Continuing...')
        except:
            print('Node connection is broken!')
            sockets[i].close()
            sockets.remove(sockets[i])
            nodesActive.remove(nodesActive[i])
    
    msg = ''

def cmdThread():
    while True:
        print('SAFEVAC Server Console')
        cmd = raw_input('$ ')
        if cmd not in commands:
            print('Invalid input')