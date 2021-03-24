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
#get timeout as argument
RetryTimeout = int(sys.argv[4])
#set up socket
sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
#set up ACK socket
ACK_socket = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
#set ip for ack sending
ACK_IP = "127.0.0.1"
#set up port
ACK_PORT = 1234
#bind to receive ACK
ACK_socket.bind((ACK_IP, ACK_PORT))
# Open the file to convert to a binary array
with open(fileToSend, 'rb') as f: 
    fr = f.read()
    image = bytearray(fr) 

# get number of full packets
fullPkts = math.floor(len(image)/1024)
#get final packet size in case image not div by 1024
finalPkt = len(image) % 1024
#set headers,retransimissions and start the timer
byteEnd = 1024
byteStart = 0
seqNum = 0
EOF = 0
retransmissions = 0
start = time.perf_counter()
for x in range(fullPkts):
    #in case last full packet is the last packet
    if x == fullPkts -1 and finalPkt == 0 :
        EOF = 1
    seqNum += 1
    pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
    
    #add header
    pkt.append(EOF)
    # Add payload
    pkt.extend(image[byteStart:byteEnd]) 
    # Send packet via specified port
    sock.sendto(pkt, (UDP_IP, UDP_PORT))
    #specify variables that are going to be used for ack
    ackRecievedCorrect = False
    ackReceived = False
    ack_seq_number = 0
    #while packet gets acknowledged
    while ackRecievedCorrect == False :
     try:
       #time out gets input in seconds while RetryTImeour is in milliseconds
       ACK_socket.settimeout(RetryTimeout/1000)
       data,addr = ACK_socket.recvfrom(2)
       ack_seq_number = int.from_bytes(data[:2],'big')
       ackReceived = True
     except socket.timeout:
         #if we get a timeout set ackReceived to False
         ackReceived = False
     
     #check that we received right ACK
     if seqNum == ack_seq_number  and ackReceived == True :
         ackRecievedCorrect = True
     #retransmit the packet
     else :
         sock.sendto(pkt, (UDP_IP, UDP_PORT))
         retransmissions += 1
      
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
    ackRecievedCorrect = False
    ackReceived = False
    ack_seq_number = 0
    
    while ackRecievedCorrect == False :
     try:
       #time out gets input in seconds while RetryTImeour is in milliseconds
       ACK_socket.settimeout(RetryTimeout/1000)
       data,addr = ACK_socket.recvfrom(2)
       ack_seq_number = int.from_bytes(data[:2],'big')
       ackReceived = True
       #if receiver has sent ack indicating it has received last packet
       if ack_seq_number == 0 :
           break
     except socket.timeout:
         #if we get a timeout set ackReceived to False
         ackReceived = False
     
     #check that we received right ACK
     if seqNum == ack_seq_number  and ackReceived == True :
         ackRecievedCorrect = True
     #retransmit the packet
     else :
         sock.sendto(pkt, (UDP_IP, UDP_PORT))
         retransmissions += 1


#get end time
end = time.perf_counter()
#get transmission time
time_finish = end - start
#get packet length in kb
image_kb = len(image) / 1024
#get rate
rate = image_kb/time_finish
print("{:d} {:0.2f}".format(retransmissions,rate))
sock.close()
