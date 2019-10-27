import socket
import sys

from gpiozero import LED
from time import sleep
from threading import Thread
from time import sleep
import RPi.GPIO as GPIO

# Alarm LED
led = LED(17)

GPIO.setup(27, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# tagid is determined by location tag that is used for the device
tagid = 1
# 0 for robot, 1 for human
is_human = 0

ALERT = False

# TCP/IP socket
server_address = ('192.168.43.184', 10000)
print('Starting Alarm Server on %s port %s' % server_address)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
sock.bind(server_address)

# Start Listening
sock.listen(1)

while True:
    try:
        # Wait for request from Server
        print('Waiting for handshake from Server')
        connection, client_address = sock.accept()
        print('connection from %s' % client_address[0])

        # Initial Handshake
        message = connection.recv(16)
        if message == b'CONNINIT':
            connection.sendall(b'CONNACK_%d_%d' % (tagid, is_human))
            print('Connection Sucessfully initilized')
        else:
            print('Server has not properly acknowledged first interaction')
        break
    except:
        print('Unable to connect to server, retrying in 5 seconds')
        sleep(1)

# Main Loop
while True:
    # Receive message from Server
    message = b''
    reply = b''
    while message == b'':
        message = connection.recv(16)
    print('received "%s"' % message)

    if GPIO.input(27) == GPIO.HIGH:
        print('Button has been pressed')
        ALERT = True

    # Update State

    data = str(message)[2:-1].split("_")

    if data[0] == 'DATAREQ':
        if ALERT:
            reply = b'PANICINIT'
        else:
            reply = b'OK'
        print('server has requested data')
    elif data[0] == 'PANICEXTERN':
        ALERT = True
        reply = b'PANIC'
        print('panic caused by exterior node')
        if data[1] == '':
            print('No navigation instruction')
        else:
            print('Navigation instruction: Go to %s' % data[1])
    elif data[0] == 'PANICCONT':
        reply = b'PANIC'
        print('Server is in panic, continuing alarm')
        if data[1] == '':
            print('No navigation instruction')
        else:
            print('Navigation instruction: Go to %s' % data[1])
    elif data[0] == 'PANICOFF':
        ALERT = False
        reply = b'OK'
        print('Server has stopped panic. Turning alarm off')
    else :
        reply = b'WRONGREQ'
        print('Unknown message received from server! Continuing...')
    
    if ALERT:
        led.on()
    else:
        led.off()
    
    print('Sending "%s"' % reply)
    connection.sendall(reply)

connection.close()