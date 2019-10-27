import socket
import sys

from time import sleep
from threading import Thread
from time import sleep
import simpleaudio as sa

ALERT = False
wave_obj = sa.WaveObject.from_wave_file("1097.wav")

# TCP/IP socket
server_address = ('127.0.0.1', 10001)
print('Starting Alarm Server on %s port %s' % server_address)
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(3)
sock.bind(server_address)

# Start Listening
sock.listen(1)

def audioThread():
    while True:
        if ALERT:
            play_obj = wave_obj.play()
            play_obj.wait_done()

audio = Thread(target=audioThread)
audio.start()

while True:
    try:
        # Wait for request from Server
        print('Waiting for handshake from Server')
        connection, client_address = sock.accept()
        print('connection from %s' % client_address[0])

        # Initial Handshake
        message = connection.recv(16)
        if message == b'CONN_INIT':
            connection.sendall(b'CONN_ACK')
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

    # Update State
    if message == b'DATA_REQ':
        if ALERT:
            reply = b'PANIC_INIT'
        else:
            reply = b'OK'
        print('server has requested data')
    elif message == b'PANIC_EXTERN':
        ALERT = True
        reply = b'PANIC'
        print('panic caused by exterior node')
    elif message == b'PANIC_CONT':
        reply = b'PANIC'
        print('Server is in panic, continuing alarm')
    elif message == b'PANIC_OFF':
        ALERT = False
        reply = b'OK'
        print('Server has stopped panic. Turning alarm off')
    else :
        reply = b'WRONG_REQ'
        print('Unknown message received from server! Continuing...')
    
    if ALERT:
        if not audio.isAlive:
            None
    
    print('Sending "%s"' % reply)
    connection.sendall(reply)

connection.close()