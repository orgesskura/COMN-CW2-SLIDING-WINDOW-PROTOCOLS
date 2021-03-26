# Orges Skura 1813106
import socket
import sys
import os
import math
import time
from threading import Thread, Timer, Lock
import queue
import select






def sendPacket(seqNum, finalSeqNum, finalPacketSize):
    if seqNum == finalSeqNum:
        EOF = 1
    else:
        EOF = 0
    if EOF != 1:
        size = 1024
    else:
        size = finalPacketSize
    pkt = bytearray(seqNum.to_bytes(2, byteorder='big'))
    pkt.append(EOF)
    start = seqNum*1024
    end = start + size
    pkt.extend(image[start:end])
    
    try: 
        sock.sendto(pkt, (UDP_IP, UDP_PORT))
    except socket.error:
        #keep sending all of the data
        select.select([],[sock],[])


def receiveAck(base):
    ackSeqNum = base
    sock.settimeout(RetryTimeout/1000)
    data, addr = sock.recvfrom(2)
    ackSeqNum = int.from_bytes(data[:2], 'big')
    if base < ackSeqNum:
        return ackSeqNum
    else:
        return receiveAck(base)




# get remote host as arg1
UDP_IP = sys.argv[1]
# geet port number
UDP_PORT = int(sys.argv[2])
# get filename as argument
fileToSend = sys.argv[3]
# get timeout as argument
RetryTimeout = int(sys.argv[4])
# get window size as argument
windowSize = int(sys.argv[5])
# set up socket
sock = socket.socket(socket.AF_INET,  socket.SOCK_DGRAM)
#set up non-blocking socket
sock.setblocking(False)
# Open the file to convert to a binary array
with open(fileToSend, 'rb') as f:
    fr = f.read()
    image = bytearray(fr)

# get number of full packets
fullPkts = math.floor(len(image)/1024)
# get final packet size in case image not div by 1024
finalPkt = len(image) % 1024
# set headers,retransimissions and start the timer
byteEnd = 1024
byteStart = 0
seqNum = 0
EOF = 0
retransmissions = 0
base = 0
#check of last ack loss
lastACklost = 0
finalSeqNum = math.ceil(float(len(image))/float(1024))
finalPacketSize = len(image) - (finalSeqNum * 1024)
start = time.perf_counter()
fileSent = False
timers_lock = Lock()

try:
	base = -1
	seqNum = 0
	finalSeqNum = math.ceil(float(len(image))/float(1024))
	finalPacketSize = len(image) - (finalSeqNum * 1024)
	fileSent = False
	while fileSent is False:
		while seqNum - base <= windowSize and seqNum <= finalSeqNum:
			sendPacket(seqNum, finalSeqNum, finalPacketSize)
			seqNum +=1
		try:
			base = receiveAck(base)
		except socket.error as exc:
			seqNum = base + 1
			retransmissions+=1
			if base == finalSeqNum:
			    fileSent = True
except socket.error as exc:
			print ("Caught exception socket.error : %s" %exc)


# get end time
end = time.perf_counter()
# get transmission time
time_finish = end - start
# get packet length in kb
image_kb = len(image) / 1024
# get rate
rate = image_kb/time_finish
print("{:0.2f}".format(rate))
sock.close()


