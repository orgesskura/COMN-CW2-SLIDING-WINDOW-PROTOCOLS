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
#Set up ACK socket
ACK_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ACK_IP = "127.0.0.1"
ACK_PORT = 1234
#create a bytearray
image = bytearray()
currSeqNum = 0
prevSeqNum = 0
while True:
    # set buffer size to 1027
    data, addr = sock.recvfrom(1027) 
    
    currSeqNum = int.from_bytes(data[:2],'big')
    if currSeqNum == (prevSeqNum + 1):
        prevSeqNum = currSeqNum
        image.extend(data[3:])
        pkt = bytearray(prevSeqNum.to_bytes(2, byteorder='big'))
        ACK_socket.sendto(pkt, (ACK_IP, ACK_PORT))
    else :
        pkt = bytearray(prevSeqNum.to_bytes(2, byteorder='big'))
        ACK_socket.sendto(pkt, (ACK_IP, ACK_PORT))
    if(data[2] == 1):
        break
    
with open(filename, 'wb') as f:
    f.write(image)

print('Transfer of image is done')
print(type(image))
sock.close()
