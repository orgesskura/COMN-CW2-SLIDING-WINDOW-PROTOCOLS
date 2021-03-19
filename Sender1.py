import socket
import sys 
import os
import math

fileToSend = sys.argv[3] # <filename>
UDP_IP = sys.argv[1]  # <remote_host> 
UDP_PORT = int(sys.argv[2]) # <port>
sock = socket.socket(socket.AF_INET, # Internet (Indication of IPv4)
                     socket.SOCK_DGRAM) # UDP

with open(fileToSend, 'rb') as f: # Open the file to convert to binary
    fr = f.read()
    byteArray = bytearray(fr) # Creates bytearray

# Number of full (1024 byte payload) packets and size of final packet. 
fullPkts = math.floor(len(byteArray)/1024)
finalPkt = len(byteArray) % 1024

byteEnd = 1024
byteStart = 0
seqNumBase10 = 0
EOF = 0
for x in range(fullPkts):
    pkt = bytearray(seqNumBase10.to_bytes(2, byteorder='big'))
    seqNumBase10 += 1
    pkt.append(EOF) # Full header created   
    pkt.extend(byteArray[byteStart:byteEnd]) # Add payload
    
    sock.sendto(pkt, (UDP_IP, UDP_PORT)) # Send packet to receiver
    
    byteStart += 1024
    byteEnd += 1024

if(finalPkt != 0): # Final packet so EOF set to 1. This only executes if we have over flow. 
    seqNumBase10 += 1
    pkt = bytearray(seqNumBase10.to_bytes(2, byteorder='big'))
    EOF = 1
    pkt.append(EOF) # Full header created
    pkt.extend(byteArray[byteStart:(byteStart+finalPkt)]) # Add payload

    sock.sendto(pkt, (UDP_IP, UDP_PORT)) # Send packet to receiver
