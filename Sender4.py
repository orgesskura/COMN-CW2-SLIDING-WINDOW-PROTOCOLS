# Orges Skura 1813106
#Generally works fine but rarely it outputs the throughput and the threads do not terminate
#File gets correctly sent and throughput is printed as well but it seems threads do not terminate
#I use os.exit to get out of this state
from socket import *
import sys
import os
import struct
import sched
import time
#import _thread
from threading import Thread,Timer, Lock
from socket import *
from enum import Enum
from collections import deque
from threading import Thread,Timer, Lock


#get arguments
UDP_IP = sys.argv[1]
UDP_PORT =int(sys.argv[2])
filename = sys.argv[3]
#divide by 1000 as i deal with seconds while input is in milliseconds
RetryTimeout = float(int(sys.argv[4])/float(1000))
windowSize = int(sys.argv[5])
#number of tries for last window
lastWindowRetries = 10
#initialize a new socket
sock = socket(AF_INET, SOCK_DGRAM)

    
#keep a list of packets to send  
packets = []
#read all the packets and put them in a list
with open(filename, 'rb') as fs:
    packet = fs.read(1024)
    while (packet):
        packets.append(packet)
        packet = fs.read(1024)
    fs.close()
#set the variables used for SR protocol
nextseqnum = 1
base = 1
#initialize variables used
timerEnable = True
#counter for keeping track of index of last packet that was sent
lastNotQueued = 0
#initialize a set used for acks
acked = set()
lastWindowAck = False
#variable to keep track of how many times tried the last window
lastWindowCount = 0
#initialize lock
lock = Lock()
#this is going to be used for a packet with all of its headers and payload
fullPackets = [None] * (len(packets) + 1)

    
#variables to keep track of timers and if transmission is done
timeoutClock = None
tranmissionComplete = False

#send packet if is in window
def send(payload, is_last):
    #declare variables
    global base
    global nextseqnum
    global timeoutClock
    global timerEnable
    global lock
    
    with lock:
        #if next packet to be sent is within window
        if(nextseqnum < base + windowSize):
            # pack everything to get it packet ready to be sent
            seq_number = struct.pack('H', nextseqnum)
            if is_last :
                eof_header = struct.pack('B', 1)
            else:
                eof_header = struct.pack('B', 0)
            fullPackets[nextseqnum] = seq_number + eof_header + payload
            sock.sendto(fullPackets[nextseqnum], (UDP_IP, UDP_PORT))
            #if base is nextSeqnum start timer
            if (base == nextseqnum):
                timerEnable = True
                timeoutClock = time.perf_counter()
            nextseqnum += 1
            return True
        else:
            return False


# thread for keeping track of acknowlegments
def receiveAck():
    global base
    global acked
    global lastWindowAck
    global timeoutClock
    global tranmissionComplete
    global timeOutThread
    global timerEnable
    global lock

    while(True):
        #if transmission is complete
        if tranmissionComplete:
            break
            
        data, addr= sock.recvfrom(2)
        ackNum = struct.unpack('H', data[0:2])[0]

        with lock:
            #add the received seq_num
            acked.add(ackNum)
            #check that we are in the last window:we cannot shift the window anymore
            if ackNum in range(len(packets) - windowSize, len(packets)+1):
                lastWindowAck = True
            
            if ackNum == base:
                allAcked = True
                #check that all packets are not acknowledged or not
                for pack in range(base, nextseqnum):
                    if pack not in acked:
                        base = pack
                        allAcked = False
                        break
                #if all acked change base
                if allAcked:
                    base = nextseqnum
                    timerEnable = False
                #else start the timer
                else:
                    timerEnable = True
                    timeoutClock = time.perf_counter()



#thread for timeouts management
def timeOutThreadMeth():
    #define these global variables to keep track of stuff
    global base
    global nextseqnum
    global lastWindowAck
    global lastWindowCount
    #maximum number of retries for last window
    global tranmissionComplete
    global lastWindowRetries
    global RetryTimeout
    global timerEnable
    global lock
    global acked
    global timeoutClock

    while(True):
        #get current time
        currentTime = time.perf_counter()
        with lock:
            #break if transmission is complete
            if tranmissionComplete:
                break
            #if timer not enabled
            if not timerEnable:
                continue
            #if packet has not timed out
            if currentTime - timeoutClock < RetryTimeout:
                continue
            else:
                #set timeoutClosk to current time
                timeoutClock = time.perf_counter()
            #if all packets have been acknowledged
            if len(packets) == len(acked):
                tranmissionComplete = True
                break
            #if we have already resent last window packets a certain nr times we break
            if lastWindowCount == lastWindowRetries:
                tranmissionComplete = True
                break
            #If we are in the last window
            if lastWindowAck:
                lastWindowCount += 1
            
            offset = 0
            #send packets up to nextseqnum
            while (base + offset < nextseqnum):
                if (base + offset >= len(fullPackets)):
                    break
                #if packet is not acked resend the packet
                if (base + offset) not in acked:
                    sock.sendto(fullPackets[base + offset], (UDP_IP, UDP_PORT))
                offset += 1


#set transmission_completee to False
tranmissionComplete = False

timeoutClock = time.perf_counter()
#assign the threads
receeiveACKThread = Thread(target=receiveAck)
timeOutThread = Thread(target=timeOutThreadMeth)
start_time = time.perf_counter()
#start the threads
receeiveACKThread.start()
timeOutThread.start()

while(not tranmissionComplete):
    #set transmission to true if packets
    if len(packets) == len(acked):
        with lock:
            tranmissionComplete = True
    #if sent all packets 
    if lastNotQueued == len(packets):
        continue
    #get next packet to be sent as index is in lastNotQueued
    nextPacket = packets[lastNotQueued]
    #if mehtod returns true increment the lastNotQueued index
    if (send(nextPacket, lastNotQueued == len(packets) - 1)):
        lastNotQueued += 1

end_time  =  time.perf_counter()
#calculate execution time
transTime = (end_time - start_time)
#get length of file to be sent
lengthFile = float(sum ([len(payload) for payload in packets])) / float(1024)
rate = lengthFile / transTime
print("{:0.2f}".format(rate))
#close socket
sock.close()
#exit when program has sent the file. Sometimes threads do not close
os._exit(0) 