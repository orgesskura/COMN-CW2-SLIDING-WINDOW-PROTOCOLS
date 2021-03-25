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
#create variables to check duplicate packets
currSeqNum = 0
prevSeqNum = 0
EOF = False
while EOF == False:
    # set buffer size to 1027 and get data from it
    data, addr = sock.recvfrom(1027)
    if data is None :
        continue
    #get sequence number of packet
    currSeqNum = int.from_bytes(data[:2],'big')
    #check that it is not a duplicate packet
    if currSeqNum == (prevSeqNum + 1):
        #increase sequence number and add to bytearray image
        prevSeqNum = currSeqNum
        image.extend(data[3:])
        pkt = bytearray(prevSeqNum.to_bytes(2, byteorder='big'))
        #send acknowledgement
        sock.sendto(pkt, addr)
    else :
        #if it is duplicate send the ACK again
        pkt = bytearray(prevSeqNum.to_bytes(2, byteorder='big'))
        sock.sendto(pkt, addr)
    #if it is last packet, break out of loop
    if(data[2] == 1):
        #send another packet indicating that receiver has the last file in case last ACK is lost
        end_number = 0
        pkt = bytearray(end_number.to_bytes(2, byteorder='big'))
        sock.sendto(pkt, addr)
        EOF = True
#write file   
with open(filename, 'wb') as f:
    f.write(image)

sock.close()
