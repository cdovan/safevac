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
server_address = ('192.168.43.185', 10000)
print ('Starting Alarm Server on %s port %s' % server_address)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)
sock.bind(server_address)

# Start Listening
sock.listen(1)

# Wait for request from Server
print ('Waiting for handshake from Server')
connection, client_address = sock.accept()
print ('connection from', client_address)

# Main Loop
while True:
    try:
        # Receive message from Server
        data = connection.recv(16)
        print ('received "%s"' % data)

        # Update State
        if data == b'ay send that data':
            if ALERT:
                connection.sendall('panic')
            else:
                connection.sendall('ok')
            print ('server has requested data')
        elif data == b'panic':
            ALERT = True
            print ('panic caused by exterior node', client_address)
        else:
            print ('server is fucked')
        
        # Reply to Server with Acknowledgement
        if ALERT:
            connection.sendall(b'ALERT_ON')
        else:
            connection.sendall(b'ALERT_OFF')

    except:
        print ("Socket timed out. Retrying...")

connection.close()