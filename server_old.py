import socket
import sys

ALERT = False

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.settimeout(10)

# Bind the socket to the port
server_address = ('192.168.43.88', 10000)
print ('Starting Alarm Server on %s port %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print ('Waiting for a connection')
    try:
        connection, client_address = sock.accept()
        print ('connection from', client_address)

        # Receive the data
        data = connection.recv(16)
        print ('received "%s"' % data)
        if data == b'ALERT_ON':
            ALERT = True
            print ('Alert message received, sending alarm')
        elif data == b'STDBY_NODE':
            print ('Handshake recieved, node is OK: ', client_address)
        elif data == b'ALERT_RESET':
            #ALERT = False
            print ('Alarm reset by node')
        else:
            print ('Unknown Transmission recieved from node!')

        if ALERT:
            connection.sendall(b'ALERT')
        else:
            connection.sendall(b'STDBY_SERVER')

        connection.close()

    except:
        print ("No signals received in 10 seconds. Continuing...")
