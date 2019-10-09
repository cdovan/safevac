import socket
import sys

from gpiozero import LED
from gpiozero import Button
from time import sleep
from threading import Thread

# Alarm LED
led = LED(17)

# Alarm Button
button = Button(27)

ALERT = False

# TCP/IP socket
server_address = ('192.168.43.184', 10000)
print('Starting Alarm Server on %s port %s' % server_address)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.bind(server_address)

# Start Listening
sock.listen(1)

# Wait for request from Server
print('Waiting for handshake from Server')
connection, client_address = sock.accept()
print('connection from', client_address)

# Initial Handshake
msg = connection.recv(16)
if msg == 'CONN_INIT':
    connection.sendall('CONN_ACK')
    print('Connection Sucessfully initilized')
else:
    print('Server has not properly acknowledged first interaction')

# Main Loop
while True:
    # Receive message from Server
    msg = ''
    while msg == '':
        msg = connection.recv(16)
    print('received "%s"' % msg)

    # Update State
    if msg == 'DATA_REQ':
        if ALERT:
            connection.sendall('PANIC')
        else:
            connection.sendall('OK')
        print('server has requested data')
    elif msg == 'PANIC_EXTERN':
        ALERT = True
        print('panic caused by exterior node', client_address)
    elif msg == 'PANIC_CONT':
        print('Server is in panic, continuing alarm')
    elif msg == 'PANIC_OFF':
        ALERT = False
        print('Server has stopped panic. Turning alarm off')
    else :
        print('Unknown message received from server! Continuing...')

connection.close()