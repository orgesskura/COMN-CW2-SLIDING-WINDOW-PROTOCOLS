# Orges Skura 1813106
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
seqNum = 0
nextSeqNum = 0
while True:
    # set buffer size to 1027 and get data from it
    data, addr = sock.recvfrom(1027) 
    #if seqNum is nextSeqnum it means we received the next in order packet
    seqNum = int.from_bytes(data[:2],'big')
    if seqNum == nextSeqNum:
        #increase sequence number and add to bytearray image
        image.extend(data[3:])
        nextSeqNum += 1
    if nextSeqNum == 0 :
        var = 0
    else :
        var = nextSeqNum - 1
    pkt = bytearray(var.to_bytes(2, byteorder='big'))
    #send acknowledgement
    sock.sendto(pkt, addr)
    #be in the loop until we receive the packet in order
    while nextSeqNum != seqNum + 1:
       # set buffer size to 1027 and get data from it
       data, addr = sock.recvfrom(1027) 
       #get sequence number of packet
       seqNum = int.from_bytes(data[:2],'big')
       #if seqNum is nextSeqnum it means we received the next in order packet
       if seqNum == nextSeqNum:
           #extend to the file
           image.extend(data[3:])
           nextSeqNum += 1
        #assign var as nextSeqnum -1 so that we can send ack to the sender for received packet
       if nextSeqNum == 0 :
            var = 0
       else :
            var = nextSeqNum - 1
       pkt = bytearray(var.to_bytes(2, byteorder='big'))
       #send acknowledgement
       sock.sendto(pkt, addr)
    #if it is last packet, break out of loop
    if(data[2] == 1):
        #send another packet indicating that receiver has the last packet in case the last ACK is lost
        pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
        sock.sendto(pkt, addr)
        break
#write file   
with open(filename, 'wb') as f:
    f.write(image)

sock.close()