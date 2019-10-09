import socket
import sys

ALERT = False

nodes = [
    '192.168.43.184',
    '192.168.43.185'
]

panicAddress = ('', 10000)

class type_t(enum):
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

sock = []

for i in range(len(nodes)):
    sock[i] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock[i].settimeout(10)

print('Connecting to all known nodes')
for i in range(len(nodes)):
    server_address = (nodes[i], 10000)
    print ('connecting to %s port %s' % server_address)
    sock[i].connect(server_address)
    sock[i].sendall('CONN_INIT')
    msg = sock[i].recv(16)
    if msg not 'CONN_ACK':
        print('Node has not acknowledged new connection! Continuing...')

while True:
    for i in sock:
        if ALERT and i.address not == panicAddress:
            i.sendall('PANIC_EXTERN')
        if ALERT and i.address == panicAddress:
            i.sendall('PANIC_CONT')
        else:
            i.sendall('DATA_REQ')

        msg = i.recv(16)
        if msg == 'PANIC':
            ALERT = True
            panicAddress = i.address
            print(i.address, ': Alert recieved')
        elif msg == 'OK':
            print(i.address, ': OK')
            if ALERT:
                i.sendall('')
                print('Sending external Alert request to node')
        else:
            print('Unknown message received from node! Continuing...')
