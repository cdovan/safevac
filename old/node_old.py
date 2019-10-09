import socket
import sys
from gpiozero import LED
from gpiozero import Button
from time import sleep
from threading import Thread

# Alarm LED
led = LED("GPIO17")

# Alarm Button
button = Button("GPIO27", pull_up=False)

ALERT = False
ALERT_RESET = False

#alarmLEDThread = Thread(target=alarmOnLED)
'''
cmd = input("Alert? y/n")
if cmd == 'y':
    ALERT = True

def alarmOnLED():
    while True:
        led.on()
        sleep(0.1)
        led.off()
        sleep(0.1)

def startAlarmLED():
    alarmLEDThread.start()

def stopAlarmLED():
    if alarmLEDThread.isAlive():
        alarmLEDThread.
'''

# Connect the socket to the port where the server is listening
server_address = ('192.168.43.88', 10000)

while True:

    if button.is_pressed:
        ALERT = True

    print(button.is_pressed)

    try:
        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)

        # Connect to Server
        print ('connecting to %s port %s' % server_address)
        sock.connect(server_address)

        # Send data
        if ALERT:
            message = b'ALERT_ON'
        else:
            message = b'STDBY_NODE'
        print ('sending "%s"' % message)
        sock.sendall(message)

        data = sock.recv(16)
        print ('received "%s"' % data)
        if data == b'ALERT':
            ALERT = True
            led.on()
            print ('Alert message recieved from server')
        elif data == b'OK':
            ALERT = False
            led.off()
            print ('OK message recieved from server')
        elif data == b'STDBY_SERVER':
            led.off()
            print ('Acknowledgement recieved from server')
        else:
            print ('Unknown message recieved from server!')

    except:
        print ("No response from server in 10 seconds. Continuing...")

    finally:
        print ('closing socket')
        sock.close()
    
    sleep(1)