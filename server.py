import socket
import sys

ALERT = False

nodes = [
    '192.168.43.184',
    '192.168.43.185'
]

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

while True:
    for i in sock:
        i.sendall('ay send that data')
        msg = i.recv(16)
        if msg == 'panic':
            ALERT
            panic()
        else:
            print('node is fucked')
