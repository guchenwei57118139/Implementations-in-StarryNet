import math
import os
#from scapy.all import *
from netfilterqueue import NetfilterQueue
import time
import socket
from multiprocessing import Pipe,Process
from threading import Thread
import threading
import asyncio
import functools
import logging
import sys
import argparse
import hmac
import hashlib
DEBUG = 0
with open('/root/starlink-Grid-LeastDelay/sd.txt','r') as f:
    lines=f.readlines()
orbit_num=eval(lines[0])
sat_num=eval(lines[1])
src=lines[2].replace('\n','')
dst=lines[3].replace('\n','')
narbs=lines[4].replace('\n','')
constellation_size = orbit_num * sat_num
Lock = threading.Lock()
server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
#server.bind(('::1', 5000))        #receive HACK

#server2 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
#server2.bind(('::1', 5000))       #receive local retransmission signal

sendd = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
os.system("ip6tables -F")
os.system("ip6tables -F -t mangle")
os.system("sysctl -w net.ipv6.conf.all.forwarding=1")

os.system("ip6tables -I OUTPUT -p icmpv6 -s "+src+"/128 -d "+dst+"/128 -j NFQUEUE --queue-num 1")
#os.system("ip6tables -I OUTPUT -p icmpv6 -d "+dst+"/128 -j NFQUEUE --queue-num 1")

#os.system("ip6tables -I OUTPUT -s "+srcaddr+"/128 -d "+dstaddr+"/128 -j NFQUEUE --queue-num 1")
#os.system("ip6tables -I INPUT -d 2001:2:1::40/128 -j NFQUEUE --queue-num 1")

#os.system("ip6tables -I OUTPUT -d 240c:c0a0:10:3055::1/128 -s 240c:c0a0:10:3116::1/128 -j NFQUEUE --queue-num 1")
#os.system("ip6tables -t mangle -A PREROUTING -d 240c:c0a0:10:3116::1/128 -p udp --dport 4000 -j NFQUEUE --queue-num 2")  #fitrst loss
#os.system("ip6tables -I OUTPUT -d ::1/128 -p udp --dport 5000 -j NFQUEUE --queue-num 3")

#t0 = time.time()
#l3no = []
hbh_header = '01020c'#00: occupied 1byte; 02:hbh header; 04 payload length
hbh_header = bytearray.fromhex(hbh_header)
##docker cp vm4-up-upstream.py lwmra_container_1:files
#
header = '60000000'
headerarray = bytearray.fromhex(header)
#narbs='0000000002040907'
#narbs='1111'
#narbs=narbs.zfill(16)
narbsarray=bytearray.fromhex(narbs)

index = 0       #Hseq number
up_handover_flag = 0        #flag = 1 means handover happens
down_handover_flag = 0      #flag = 1 means handover happens
pre_hack_no = 0     #recent HACK number

#
new_nex_header = hex(0)
new_nex_header = new_nex_header[2:]
new_nex_header = new_nex_header.zfill(2)
def pack(pkt):
    #t0 = time.time()
    global index,maxx,new_nex_header,up_handover_flag,down_handover_flag
    #if pkt.get_mark()!=1:
    
    pld = pkt.get_payload()
#    Lock.acquire()
#    if index==maxx:
#        index = 0
#    seq = index
#    if DEBUG:
#        print('send',seq)
#    index += 1
#    Lock.release()
    payload = bytearray()
    payload.extend(pld[:4])
    payload.extend(bytes.fromhex(hex(int.from_bytes(pld[4:6], 'big') + 16)[2:].zfill(4)))#payload length+8bytes
    payload.extend(bytes.fromhex(new_nex_header))
    payload.extend(pld[7:40])
    payload.extend(pld[6:7])
    payload.extend(hbh_header)
    payload.extend(narbsarray)
    payload.extend(pld[40:])
    pld = bytes(payload)
    pkt.set_payload(pld)
    pkt.accept()
 
class NFQueue3(object):
    def __init__(self, queue, cb, *cb_args, **cb_kwargs):
        self.logger = logging.getLogger('NFQueue3#{}'.format(queue))
        self.logger.info('Bind queue #{}'.format(queue))
        self._loop = asyncio.get_event_loop()
        asyncio.set_event_loop(self._loop)

        self.queue = queue
        # Use packet counter
        self.counter = 0
        # Create NetfilterQueue object
        self._nfqueue = NetfilterQueue()
        # Bind to queue and register callbacks
        self.cb = cb
        self.cb_args = cb_args
        self.cb_kwargs = cb_kwargs
        self._nfqueue.bind(self.queue, self._nfcallback,max_len=2048)
        # Register queue with asyncio
        self._nfqueue_fd = self._nfqueue.get_fd()
        # Create callback function to execute actual nfcallback
        cb2 = functools.partial(self._nfqueue.run, block=False)
        self._loop.add_reader(self._nfqueue_fd, cb2)

    def _nfcallback(self, pkt):
        self.counter += 1
        if self.cb is None:
            data = pkt.get_payload()
            self.logger.debug('Received ({} bytes): {}'.format(len(data), data))
            pkt.accept()
            return

        cb, args, kwargs = self.cb, self.cb_args, self.cb_kwargs
        cb(pkt, *args, **kwargs)

    def set_callback(self, cb, *cb_args, **cb_kwargs):
        self.logger.info('Set callback to {}'.format(cb))
        self.cb = cb
        self.cb_args = cb_args
        self.cb_kwargs = cb_kwargs

    def terminate(self):
        self.logger.info('Unbind queue #{}: received {} pkts'.format(self.queue, self.counter))
        self._loop.remove_reader(self._nfqueue_fd)
        self._nfqueue.unbind()
if __name__ == '__main__':

    out_pipe, in_pipe = Pipe()
    #Process(target=func, args=(out_pipe, in_pipe, pre_hack_no, )).start()

    # Instantiate loop
    loop = asyncio.get_event_loop()
#    asyncio.set_event_loop(loop)
    # Create NFQueue3 objects
    queues = []
#    queues.append(NFQueue3(1, func_right))
#    queues.append(NFQueue3(2, func_up)
    queues.append(NFQueue3(1, pack))

    try:
        loop.run_forever()
#        asyncio.get_running_loop()
    except KeyboardInterrupt:
        pass
    for q in queues:
        q.terminate()
    loop.close()
os.system("ip6tables -F")
os.system("ip6tables -F -t mangle")
#def pack(pkt):
#    #t0 = time.time()
#    scapy_packet = IP(pkt.get_payload())
#
#    global index,maxx,new_nex_header,up_handover_flag,down_handover_flag
#    if pkt.get_mark()!= 1:
#        pld = pkt.get_payload()
#        #print(pld)
#        Lock.acquire()
#        if index==maxx:
#            index = 0
#        seq = index
#        if DEBUG:
#            print('send',seq)
#        index += 1
#        Lock.release()
#        payload = bytearray()
#        payload.extend(pld[:4])
#        payload.extend(bytes.fromhex(hex(int.from_bytes(pld[4:6], 'big') + 8)[2:].zfill(4)))#payload length+8
#        payload.extend(bytes.fromhex(new_nex_header))
#        payload.extend(pld[7:40])
#        payload.extend(pld[6:7])
#        payload.extend(hbh_header)
#        payload.extend(l3no[seq])
#        payload.extend(pld[40:])
#        pld = bytes(payload)
#        pkt.set_payload(pld)
#        cache[seq]=pld
#
#    pkt.accept()
#
#def retran(pkt,in_pipe):
#    pld = pkt.get_payload()
#    in_pipe.send_bytes(pld[48:])
#    pkt.drop()
#'''
#def udp_to_data(pkt):
#    global index,pre_hack_no
#    pld = pkt.get_payload()
#    loss = pld[48:]
#    loss_no = int(loss.hex(),16)
#    pld = bytes(cache[loss_no])
#    pkt.set_mark(1)
#    pkt.set_payload(pld)
#    #pkt.set_payload(cache[loss_no])
#    if pre_hack_no.value==0 and DEBUG:
#        print('retran',index,pre_hack_no.value)
#    pkt.accept()
#'''
#def udp_to_data(pkt):
#    global index
#    Lock.acquire()
#    if index==maxx:
#       index = 0
#    seq = index
#    index += 1
#    Lock.release()
#    pld = pkt.get_payload()
#    loss = pld[48:]
#    loss_no = int(loss.hex(),16)
#    if DEBUG:
#        #pass
#        print('retrans ',loss_no)
#    pldarray = bytearray(cache[loss_no])
#    hbh = l3no[seq]
#    payload = pldarray[:41] + hbh_header + hbh + pldarray[48:]
#    pld = bytes(payload)
#    pkt.set_payload(pld)
#    cache[seq]=pld
#    #pkt.set_payload(cache[loss_no])
#    pkt.accept()
#
#class NFQueue3(object):
#    def __init__(self, queue, cb, *cb_args, **cb_kwargs):
#        self.logger = logging.getLogger('NFQueue3#{}'.format(queue))
#        self.logger.info('Bind queue #{}'.format(queue))
#        self._loop = asyncio.get_event_loop()
#        self.queue = queue
#        # Use packet counter
#        self.counter = 0
#        # Create NetfilterQueue object
#        self._nfqueue = NetfilterQueue()
#        # Bind to queue and register callbacks
#        self.cb = cb
#        self.cb_args = cb_args
#        self.cb_kwargs = cb_kwargs
#        self._nfqueue.bind(self.queue, self._nfcallback,max_len=2048)
#        # Register queue with asyncio
#        self._nfqueue_fd = self._nfqueue.get_fd()
#        # Create callback function to execute actual nfcallback
#        cb2 = functools.partial(self._nfqueue.run, block=False)
#        self._loop.add_reader(self._nfqueue_fd, cb2)
#
#    def _nfcallback(self, pkt):
#        self.counter += 1
#        if self.cb is None:
#            data = pkt.get_payload()
#            self.logger.debug('Received ({} bytes): {}'.format(len(data), data))
#            pkt.accept()
#            return
#
#        cb, args, kwargs = self.cb, self.cb_args, self.cb_kwargs
#        cb(pkt, *args, **kwargs)
#
#    def set_callback(self, cb, *cb_args, **cb_kwargs):
#        self.logger.info('Set callback to {}'.format(cb))
#        self.cb = cb
#        self.cb_args = cb_args
#        self.cb_kwargs = cb_kwargs
#
#    def terminate(self):
#        self.logger.info('Unbind queue #{}: received {} pkts'.format(self.queue, self.counter))
#        self._loop.remove_reader(self._nfqueue_fd)
#        self._nfqueue.unbind()
#
#if __name__ == '__main__':
#
#    pre_hack_no = 0
#    out_pipe, in_pipe = Pipe()
#    Process(target=func, args=(out_pipe, in_pipe, pre_hack_no, )).start()
#
#    # Instantiate loop
#    loop = asyncio.get_event_loop()
#    # Create NFQueue3 objects
#    queues = []
#    queues.append(NFQueue3(1, pack))
#    queues.append(NFQueue3(2, retran, in_pipe))
#    queues.append(NFQueue3(3, udp_to_data))
#    try:
#        loop.run_forever()
#    except KeyboardInterrupt:
#        pass
#    for q in queues:
#        q.terminate()
#    loop.close()
#os.system("ip6tables -F")
#os.system("ip6tables -F -t mangle")




