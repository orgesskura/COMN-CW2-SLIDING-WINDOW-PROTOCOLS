# Orges Skura 1813106
import socket
import sys 
import os
import math
import time

# get remote host as arg1
UDP_IP = sys.argv[1]
# geet port number
UDP_PORT = int(sys.argv[2]) 
#get filename as argument
fileToSend = sys.argv[3]

#set up socket
sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM) 
# Open the file to convert to a binary array
with open(fileToSend, 'rb') as f: 
    fr = f.read()
    image = bytearray(fr) 

# get number of full packets
fullPkts = math.floor(len(image)/1024)
finalPkt = len(image) % 1024

byteEnd = 1024
byteStart = 0
seqNum = 0
EOF = 0
for x in range(fullPkts):
    #in case last full packet is the last packet
    if x == fullPkts -1 and finalPkt == 0 :
        EOF = 1

    pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
    seqNum += 1
    #add header
    pkt.append(EOF)
    # Add payload
    pkt.extend(image[byteStart:byteEnd]) 
    # Send packet via specified port
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    time.sleep(0.01)
    
    byteStart += 1024
    byteEnd += 1024
# Final packet so EOF set to 1. This only executes if we have over flow.
if(finalPkt != 0):  
    seqNum += 1
    pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
    EOF = 1
    # Full header created
    pkt.append(EOF)
    # Add payload
    pkt.extend(image[byteStart:(byteStart+finalPkt)]) 
    # Send packet to receiver
    sock.sendto(pkt, (UDP_IP, UDP_PORT))

sock.close()
