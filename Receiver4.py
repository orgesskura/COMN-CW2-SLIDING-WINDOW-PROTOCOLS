#Orges Skura 1813106
from socket import *
import sys
import math
import time
import struct
from enum import Enum


#get arguments
UDP_Port = int(sys.argv[1])
filename = sys.argv[2]
#the program works for only windows size that is same to sender's window size as outlined in the lectures
windowSize = int(sys.argv[3])
UDP_IP = '127.0.0.1'
#create and assign socket
sock = socket(AF_INET, SOCK_DGRAM)
sock.bind((UDP_IP,UDP_Port))

    
#image will be used to write the image received
image = bytearray()
#dictionary to assign seqNum as keys to data of that packet as value
seqToPacket = dict()
#set finalSeqNum as 2^16 as that is maximum it can be held in 2 bytees
finalSeqNum = pow(2, 16)
#var indicate that receeiver is listening
listen = True
last_packet_ack = None
#set base for receiver
receiveBase = 1
packets = struct.pack('H', 0)
#assign boolean variables
lastReceived = False
isLast = False
sendAddress = None
while listen:
    #if base is greater than finalSeqNum wee ebreak
    if receiveBase > finalSeqNum:
        listen = False
        break
    #listen to geet data
    data, addr = sock.recvfrom(1027)

    #See if its end of file
    if data[2] == 1 :
        isLast = True
    #change sendAddress
    if not sendAddress:
        sendAddress = addr

    #unpack seqnum
    seqNum = struct.unpack('H', data[0:2])[0]
    #if last packet set the vars accordingly
    if isLast:
        finalSeqNum = seqNum
        lastReceived = True
    #if seqnum is in previos base - windowSize: send an ACK
    if seqNum in range(receiveBase - windowSize, receiveBase):
        packets = struct.pack('H', seqNum)
        sock.sendto(packets, sendAddress)
    #if seqnum is in window, add to dictionary and send ACK
    if (seqNum >= receiveBase and seqNum < receiveBase + windowSize):
        packetData = data[3:]
        packets = struct.pack('H', seqNum)
        sock.sendto(packets, sendAddress)
        seqToPacket[seqNum] = packetData
    
        #if seqNum is equal to base : check that all of packets within window are ACKed
        if seqNum == receiveBase:
            allAcked = True
            for windowPacket in range(receiveBase, receiveBase + windowSize):
                if not windowPacket in seqToPacket:
                    #this means we do not have a complete window and this is the first seq number, so assign base as this number and break
                    receiveBase = windowPacket
                    allAcked = False
                    break
                else:
                    #if we have a complete window add to image file
                    image += seqToPacket[windowPacket]
            if allAcked:
                # if we have complete window, shift the window and add to the base
                receiveBase += windowSize

#have an ACK window for all ACK to be sent. It will hold tuples of seqnum and packet of seqnum. This is only for the last window
ACKWindow = []
for seq_num in range(0, windowSize):
    #if not in last seqNum append the tuples to the ACKWindow
    if finalSeqNum - seq_num >= 1:
        ACKWindow.append((finalSeqNum - seq_num, struct.pack('H',finalSeqNum-seq_num)))
#send ACK's five times to make sure sender gets all of them
for i in range(5):
    #have a short sleep to have time between different iterations to make sure the ACK's go to the sender
    time.sleep(40/1000)
    #sort the list of tuples on the first element and send those packets
    for (seqNum, packet) in sorted(ACKWindow, key=lambda x: x[0]):
        sock.sendto(packet, sendAddress)

#write image
with open(filename, 'wb') as f:
    f.write(image)
    f.close()
#closee socket
sock.close()