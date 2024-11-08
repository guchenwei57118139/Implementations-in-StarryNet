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
parser = argparse.ArgumentParser()
parser.add_argument('-o', type=int, default = None)
parser.add_argument('-s', type=int, default = None)
parser.add_argument('-dst', type=str, default = None)
parser.add_argument('-narbs', type=str, default = None)
parser.add_argument('-src', type=str, default = None)
parser.add_argument('-me', type=int, default = None)
args = parser.parse_args()

orbit_num=args.o
sat_num=args.s
constellation_size = orbit_num * sat_num

server = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
sendd = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)

os.system("ip6tables -F")
os.system("ip6tables -F -t mangle")
os.system("sysctl -w net.ipv6.conf.all.forwarding=1")
dstaddr=args.dst+'/128'
srcaddr=args.src+'/128'
#os.system("ip6tables -I FORWARD -s "+srcaddr+" -d "+dstaddr+" -j NFQUEUE --queue-num 2")
#os.system("ip6tables -I FORWARD -p icmpv6 -s "+srcaddr+" -d "+dstaddr+" -j NFQUEUE --queue-num 2")
os.system("ip6tables -I FORWARD -p icmpv6 -d "+dstaddr+" -j NFQUEUE --queue-num 2")

#os.system("ip6tables -I FORWARD -d "+dstaddr+" -j NFQUEUE --queue-num 2")

hbh_header='01020c'
hbh_header = bytearray.fromhex(hbh_header)
narbs=args.narbs#'000000000102010300000000'

narbsarray=bytearray.fromhex(narbs)
# print(narbsarray)
me=args.me
index = 0       #Hseq number
up_handover_flag = 0        #flag = 1 means handover happens
down_handover_flag = 0      #flag = 1 means handover happens
pre_hack_no = 0     #recent HACK number
#maxx = 2**24
#cache=[0 for i in range(1,int(math.pow(2,24)))]
#handover_cache=[0 for i in range(1,int(math.pow(2,24)))]
#
new_nex_header = hex(0)
new_nex_header = new_nex_header[2:]
new_nex_header = new_nex_header.zfill(2)
#read config files

file=open('/root/starlink-Grid-LeastDelay/network.txt','r')
network=eval(file.readline())
file.close()
#file_log=open('log.txt','a')
flag=0#用于判断是否已经配置过路由表了
def get_satno(idx):
    plane=idx//sat_num+1 #[1,24]
    sat_no=(idx+1)%sat_num
    sat_no=sat_num if sat_no==0 else sat_no
    return [int(plane),int(sat_no)]
def pack(pkt):
    #t0 = time.time()
    global index,maxx,new_nex_header,up_handover_flag,down_handover_flag
    #if pkt.get_mark()!=1:
    pld = pkt.get_payload()
    Lock.acquire()
    if index==maxx:
        index = 0
    seq = index
    if DEBUG:
        print('send',seq)
    index += 1
    Lock.release()
    payload = bytearray()
    payload.extend(pld[:4])
    payload.extend(bytes.fromhex(hex(int.from_bytes(pld[4:6], 'big') + 40)[2:].zfill(4)))#payload length+8bytes
    payload.extend(bytes.fromhex(new_nex_header))
    payload.extend(pld[7:40])
    #payload.extend(pld[6:7])
    #payload.extend(hbh_header)
    payload.extend(narbsarray)
    payload.extend(pld[40:])
    pld = bytes(payload)
    pkt.set_payload(pld)
   #cache[seq]=pld
    pkt.accept()
def func_right(pkt):
    global flag
#先添加路由 ip -6 add xxxxx
#    file_log.write(f'start_time:{str(time.now())}\n')
#    print('start time: '+str(time.time()))
#    file=open('myself.txt','r')
#    me=eval(file.readline())
#    file.close()
    dsid=eval(args.dst.split(':')[2])
    tp,ts=get_satno(dsid)
    left_sat_id=me-sat_num if me-sat_num>=0 else constellation_size+me-sat_num
    right_sat_id=(me+sat_num)%constellation_size
    up_sat_id=me+1
    down_sat_id=me-1
    if down_sat_id%sat_num ==sat_num-1:
        down_sat_id=me-1+sat_num
    if up_sat_id%sat_num==0:
        up_sat_id=me+1-sat_num
    left_ipv6="2001:"+str(left_sat_id)+":"+str(me)+"::"
    right_ipv6="2001:"+str(me)+":"+str(right_sat_id)+"::"
    up_ipv6="2001:"+str(me)+":"+str(up_sat_id)+"::"
    down_ipv6="2001:"+str(down_sat_id)+":"+str(me)+"::"
    l=str(left_sat_id)+":"+str(me)
    r=str(me)+":"+str(right_sat_id)
    u=str(me)+":"+str(up_sat_id)
    d=str(down_sat_id)+":"+str(me)
    orbit,sat_no=get_satno(me)
    pld=pkt.get_payload()
    narbs=pld[44:52]
    #down eht1 up eth2 right eth3 left eth4
#    l_N=int.from_bytes(narbs[0],'big')
#    r_N=int.from_bytes(narbs[1],'big')
#    u_N=int.from_bytes(narbs[2],'big')
#    d_N=int.from_bytes(narbs[3],'big')
#    l_S=int.from_bytes(narbs[4],'big')
#    r_S=int.from_bytes(narbs[5],'big')
#    u_S=int.from_bytes(narbs[6],'big')
#    d_S=int.from_bytes(narbs[7],'big')
    l_N=narbs[0]
    r_N=narbs[1]
    u_N=narbs[2]
    d_N=narbs[3]
    l_S=narbs[4]
    r_S=narbs[5]
    u_S=narbs[6]
    d_S=narbs[7]
#    file_log.write(f'write_table_time:{str(time.now())}\n')
#    print('table time: '+str(time.time()))
#    print(l_N,r_N,u_N,u_S)
    if flag==1:
        pkt.accept()
    else:
        if ((orbit>l_N and orbit<r_N) and (sat_no==u_N or sat_no==d_N))\
        or ((orbit>l_S and orbit<r_S) and (sat_no==u_S or sat_no==d_S)):
            if sat_no==d_N and (ts==22 or ts<sat_no):
                os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[down_sat_id][d]['addr']+' dev '+network[me][d]['eth']+' metric 10 pref high')
            else:
                os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[right_sat_id][r]['addr']+' dev '+network[me][r]['eth']+' metric 10 pref high')
        elif (orbit==l_N  and (sat_no<u_N and sat_no>d_N))\
        or (orbit==l_S  and (sat_no>u_S and sat_no<d_S)):
            os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[down_sat_id][d]['addr']+' dev '+network[me][d]['eth']+' metric 10 pref high')
        elif (orbit==l_N and (sat_no==u_N or sat_no==d_N))\
        or (orbit==l_S and (sat_no==u_S or sat_no==d_S)):
            os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[right_sat_id][r]['addr']+' dev '+network[me][r]['eth']+' metric 10 pref high')
        elif (orbit==r_N and sat_no==u_N):
            os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[down_sat_id][d]['addr']+' dev '+network[me][d]['eth']+' metric 10 pref high')
#        elif (orbit==r_N and sat_no==d_N):
#            if (ts==22 or ts<sat_no):
#                os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[down_sat_id][d]['addr']+' dev '+network[me][d]['eth']+' metric 10 pref high')
        elif (orbit==r_N  and (sat_no<u_N and sat_no>d_N))\
        or (orbit==r_S  and (sat_no>u_S and sat_no<d_S)):
            if(tp>orbit):
                os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[right_sat_id][r]['addr']+' dev '+network[me][r]['eth']+' metric 10 pref high')
            else:
                os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[down_sat_id][d]['addr']+' dev '+network[me][d]['eth']+' metric 10 pref high')
#        if ((orbit>=l_N and orbit<=r_N) and (sat_no==u_N or sat_no==d_N))\
#        or ((orbit>=l_S and orbit<=r_S) and (sat_no==u_S or sat_no==d_S)):
#            os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[right_sat_id][r]['addr']+' dev '+network[me][r]['eth']+' metric 10 pref high')
#        if ((orbit==l_N or orbit==r_N) and (sat_no<u_N and sat_no>d_N))\
#        or ((orbit==l_S or orbit==r_S) and (sat_no>u_S and sat_no<d_S)):
#            os.system('ip -6 route add '+dstaddr[0:-4]+'/112 via '+network[down_sat_id][d]['addr']+' dev '+network[me][d]['eth']+' metric 10 pref high')
        flag=1
        pkt.accept()
#    file_log.write(f'end_time:{str(time.now())}\n')
#    print('end time: '+str(time.time()))
def func_up(pkt):
    file=open('myself.txt','r')
    me=eval(file.readline())
    file.close()
    left_sat_id=me-sat_num if me-sat_num!=0 else constellation_size
    right_sat_id=(me+sat_num)%constellation_size
    up_sat_id=me+1
    down_sat_id=me-1
    network={}
    file=open('network.txt','r')
    network=eval(file.readline())
    file.close()
    l=str(str(me)+":"+str(left_sat_id))
    r=str(right_sat_id)+":"+str(me)
    u=str(up_sat_id)+":"+str(me)
    d=str(me)+":"+str(down_sat_id)
    orbit=(me-1)//sat_num+1
    sat_no=(me)%sat_num
    sat_no=sat_num if sat_no==0 else sat_no
    pld=pkt.get_payload()
    narbs=pld[44:52]
    #down eht1 up eth2 right eth3 left eth4
    
#    l_N=int.from_bytes(narbs[0],'big')
#    r_N=int.from_bytes(narbs[1],'big')
#    u_N=int.from_bytes(narbs[2],'big')
#    d_N=int.from_bytes(narbs[3],'big')
#    l_S=int.from_bytes(narbs[4],'big')
#    r_S=int.from_bytes(narbs[5],'big')
#    u_S=int.from_bytes(narbs[6],'big')
#    d_S=int.from_bytes(narbs[7],'big')
    l_N=narbs[0]
    r_N=narbs[1]
    u_N=narbs[2]
    d_N=narbs[3]
    l_S=narbs[4]
    r_S=narbs[5]
    u_S=narbs[6]
    d_S=narbs[7]
    print(l_N,r_N,u_N,d_N,l_S,r_S,u_S,d_S)

    if ((orbit==l_N or orbit==r_N) and (sat_no<u_N or sat_no>d_N))\
    or ((orbit==l_S and orbit==r_S) and (sat_no>u_S or sat_no<d_S)):
        os.system('ip -6 route add '+dstaddr+' via'+network[u]['addr'])
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
    queues.append(NFQueue3(2, func_right))
#    queues.append(NFQueue3(3, func_up))

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





