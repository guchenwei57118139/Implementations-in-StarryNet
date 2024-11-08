import math
import os,signal
import re
import subprocess
#from netfilterqueue import NetfilterQueue
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
def process(me):
    #for line in os.popen("ip netns exec "+me+" ps ax | grep python3 | grep -v grep"):
    for line in os.popen("ps ax | grep python3 | grep -v grep"):
        fields = line.split()

        # extracting Process ID from the output
        pid = fields[0]

        # terminating process
        os.kill(int(pid), signal.SIGKILL)
nodes=[[266, 288, 310, 332, 354, 376, 398],[266, 288, 287, 309, 331, 353, 375, 397, 398],[312, 311, 310, 309, 308, 330, 352, 374],[312, 334, 356, 378, 377, 376, 375, 374],[356, 355, 354, 353, 352, 373, 395, 417, 439, 461, 483, 505],[356, 378, 400, 422, 444, 466, 488, 487, 509, 508, 507, 506, 484, 505]]
with open('/root/starlink-Grid-LeastDelay/sd.txt','r') as f:
    lines=f.readlines()
orbit_num=eval(lines[0])
sat_num=eval(lines[1])
src=lines[2].replace('\n','')
dst=lines[3].replace('\n','')
narbs=lines[4].replace('\n','')
constellation_size=orbit_num*sat_num
ssid=-1
if dst=='2001:376:398::40':
    ssid=266
    nodes=[[288, 310, 332, 354, 376, 398],[288, 287, 309, 331, 353, 375, 397, 398],[311, 310, 309, 308, 330, 352, 374],[334, 356, 378, 377, 376, 375, 374]]
elif dst=='2001:352:374::40':
    ssid=312
    nodes=[[334,356,355,354,353,352,374,356,357,378,377,399,376,375,374,397,356, 355, 354, 353, 352, 373, 395, 417, 439, 461, 483, 505]]


def get_satno(idx):
    plane=idx//sat_num+1 #[1,24]
    sat_no=(idx+1)%sat_num
    sat_no=sat_num if sat_no==0 else sat_no
    return [int(plane),int(sat_no)]
forward_nodes=set()
for sats in nodes:
    for sid in sats:
        forward_nodes.add(sid)
#file=open('/root/starlink-Grid-LeastDelay/network.txt','r')
#network=eval(file.readline())
#file.close()
dst=dst.split(':')
prefix=dst[0]+':'+dst[1]+":"+dst[2]+"::"
for me in range(200,600):#forward_nodes:
    p,s=get_satno(me)
    sid='SH1O'+str(p)+'S'+str(s)
    os.system("ip netns exec "+sid+" ip6tables -F")
    os.system("ip netns exec "+sid+" ip6tables -F -t mangle")
#    left_sat_id=me-sat_num if me-sat_num>=0 else constellation_size+me-sat_num
#    right_sat_id=(me+sat_num)%constellation_size
#    up_sat_id=me+1
#    down_sat_id=me-1
#    if down_sat_id%sat_num ==sat_num-1:
#        down_sat_id=me-1+sat_num
#    if up_sat_id%sat_num==0:
#        up_sat_id=me+1-sat_num
#    left_ipv6="2001:"+str(left_sat_id)+":"+str(me)+"::"
#    right_ipv6="2001:"+str(me)+":"+str(right_sat_id)+"::"
#    up_ipv6="2001:"+str(me)+":"+str(up_sat_id)+"::"
#    down_ipv6="2001:"+str(down_sat_id)+":"+str(me)+"::"
#    l=str(left_sat_id)+":"+str(me)
#    r=str(me)+":"+str(right_sat_id)
#    u=str(me)+":"+str(up_sat_id)
#    d=str(down_sat_id)+":"+str(me)
#    orbit,sat_no=get_satno(me)
    
    s='ip netns exec '+sid+' ip -6 route | grep \''+prefix+'/112 via\' | head -n 10'
    with os.popen(s) as f:
        for ls in f:
            if(re.match(".*metric 10 pref high$",ls)):
                os.system('ip netns exec '+sid+' ip -6 route del '+ls)

process(sid)
#
