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
message = connection.recv(16)
if message == 'CONN_INIT':
    connection.sendall('CONN_ACK')
    print('Connection Sucessfully initilized')
else:
    print('Server has not properly acknowledged first interaction')

# Main Loop
while True:
    # Receive message from Server
    message = ''
    reply = ''
    while message == '':
        message = connection.recv(16)
    print('received "%s"' % message)

    # Update State
    if message == 'DATA_REQ':
        if ALERT:
            reply = 'PANIC_INIT'
        else:
            reply = 'OK'
        print('server has requested data')
    elif message == 'PANIC_EXTERN':
        ALERT = True
        reply = 'PANIC'
        print('panic caused by exterior node', client_address)
    elif message == 'PANIC_CONT':
        reply = 'PANIC'
        print('Server is in panic, continuing alarm')
    elif message == 'PANIC_OFF':
        ALERT = False
        reply = 'OK'
        print('Server has stopped panic. Turning alarm off')
    else :
        reply = 'WRONG_REQ'
        print('Unknown message received from server! Continuing...')
    
    print('Sending "%s"' % reply)
    connection.sendall(reply)

connection.close()