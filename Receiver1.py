# Orges Skura 1813106
import socket
import socket
import sys 
import os
import math

# specify localhost
UDP_IP = "127.0.0.1"
#speecify port
UDP_PORT = int(sys.argv[1])
#specify filename to be created
filename = sys.argv[2] 
#start a socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Use this socket for specified port number
sock.bind((UDP_IP, UDP_PORT)) 
#create a bytearray
image = bytearray()

while True:
    # set buffer size to 1027 and receive data
    data, addr = sock.recvfrom(1027)
    #add to image bytearray
    image.extend(data[3:]) 
    #if it is last packet break
    if(data[2] == 1):
        break

#write image    
with open(filename, 'wb') as f:
    f.write(image)


sock.close()
