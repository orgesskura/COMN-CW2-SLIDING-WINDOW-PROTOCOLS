import socket
import socket
import sys 
import os
import math

UDP_IP = "127.0.0.1" # Local host 
UDP_PORT = int(sys.argv[1]) # <port>
filename = sys.argv[2] # <filename>

sock = socket.socket(socket.AF_INET, # Internet (Indication of IPv4)
                     socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT)) # We have to bind the IP host address to this port because it tells us which port we should send incoming packets too. 

image = bytearray()

while True:
    data, addr = sock.recvfrom(1027) # buffer size set to 1027
    image.extend(data[3:]) 

    if(data[2] == 1):
        break
    
with open(filename, 'wb') as f:
    f.write(image)

print('Image transfer done!')
print(type(image))
