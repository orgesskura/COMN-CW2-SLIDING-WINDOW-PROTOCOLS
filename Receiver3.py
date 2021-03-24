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
#set up IP and PORT. Choice of port is random. That port can not be used to transfer image
ACK_IP = "127.0.0.1"
ACK_PORT = UDP_PORT + 1
#create a bytearray
image = bytearray()
#create variables to check duplicate packets
seqNum = 0
nextSeqNum = 0
while True:
    # set buffer size to 1027 and get data from it
    data, addr = sock.recvfrom(1027) 
    #get sequence number of packet
    seqNum = int.from_bytes(data[:2],'big')
    #check that it is not a duplicate packet
    if seqNum == nextSeqNum:
        #increase sequence number and add to bytearray image
        image.extend(data[3:])
        nextSeqNum += 1
    var = nextSeqNum - 1
    pkt = bytearray(var.to_bytes(2, byteorder='big'))
    #send acknowledgement
    ACK_socket.sendto(pkt, (ACK_IP, ACK_PORT))
    while nextSeqNum != seqNum + 1:
       # set buffer size to 1027 and get data from it
       data, addr = sock.recvfrom(1027) 
       #get sequence number of packet
       seqNum = int.from_bytes(data[:2],'big')
       if seqNum == nextSeqNum:
           image.extend(data[3:])
           nextSeqNum += 1
       var = nextSeqNum - 1
       pkt = bytearray(var.to_bytes(2, byteorder='big'))
       #send acknowledgement
       ACK_socket.sendto(pkt, (ACK_IP, ACK_PORT))
    #if it is last packet, break out of loop
    if(data[2] == 1):
        #send another packet indicating that receiver has the last packet in case the last ACK is lost
        end_number = 0
        pkt = bytearray(end_number.to_bytes(2, byteorder='big'))
        ACK_socket.sendto(pkt, (ACK_IP, ACK_PORT))
        break
#write file   
with open(filename, 'wb') as f:
    f.write(image)

sock.close()
ACK_socket.close()
