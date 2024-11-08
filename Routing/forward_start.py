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
with open('/root/starlink-Grid-LeastDelay/sd.txt','r') as f:
    lines=f.readlines()
orbit_num=eval(lines[0])
sat_num=eval(lines[1])
src=lines[2].replace('\n','')
dst=lines[3].replace('\n','')
narbs=lines[4].replace('\n','')
#parser.add_argument('-o', type=int, default = None)
#parser.add_argument('-s', type=int, default = None)
#parser.add_argument('-dst', type=str, default = None)
#parser.add_argument('-narbs', type=str, default = None)
#parser.add_argument('-src', type=str, default = None)
#parser.add_argument('-me', type=int, default = None)
#args = parser.parse_args()
#
#orbit_num=args.o
#sat_num=args.s
constellation_size = orbit_num * sat_num
def get_satno(idx):
    plane=idx//sat_num+1 #[1,24]
    sat_no=(idx+1)%sat_num
    sat_no=sat_num if sat_no==0 else sat_no
    return [int(plane),int(sat_no)]
nodes=[[288, 310, 332, 354, 376, 398],[288, 287, 309, 331, 353, 375, 397, 398],[311, 310, 309, 308, 330, 352, 374],[334, 356, 378, 377, 376, 375, 374],[356, 355, 354, 353, 352, 373, 395, 417, 439, 461, 483, 505],[356, 378, 400, 422, 444, 466, 488, 487, 509, 508, 507, 506, 484, 505]]
ssid=-1
if dst=='2001:376:398::40':
    ssid=266
    nodes=[[288, 310, 332, 354, 376, 398],[288, 287, 309, 331, 353, 375, 397, 398],[311, 310, 309, 308, 330, 352, 374],[334, 356, 378, 377, 376, 375, 374]]
elif dst=='2001:352:374::40':
    ssid=312
    nodes=[[334,356,355,354,353,352,374,356,357,378,377,376,375,374]]
elif dst=='2001:483:505::40':
    ssid=356
    nodes=[[356, 378, 400, 422, 444, 466, 488, 487, 509, 508, 507, 506, 484, 505,399,421,443,465,]]
elif dst=='2001:528:529::40':
    ssid=309
    nodes=[[309, 331, 353, 375, 397, 419, 441, 463, 485, 507, 529,309, 331, 330, 352, 374, 396, 418, 440, 462, 484, 506, 528, 529]]
elif dst=='2001:507:529::40':
    ssid=266
    nodes=[[266, 265, 287, 309, 331, 353, 375, 397, 419, 441, 463, 485, 507, 529,309, 331, 353, 375, 397, 419, 441, 463, 485, 507, 529,309, 331, 330, 352, 374, 396, 418, 440, 462, 484, 506, 528, 529,288, 287, 286, 308, 330, 352, 374, 396, 418, 440, 462, 484, 506, 528, 529,288, 310, 332, 354, 376, 398]]
forward_nodes=set()
for sats in nodes:
    for sid in sats:
        forward_nodes.add(sid)

for sid in forward_nodes:
    if sid ==ssid:continue
    p,s=get_satno(sid)
    me='SH1O'+str(p)+'S'+str(s)
    os.system('ip netns exec '+me+' python3 /root/starlink-Grid-LeastDelay/forward.py -o '+str(orbit_num)+' -s '+str(sat_num)+' -src '+src+' -dst '+dst+' -narbs '+str(narbs)+' -me '+str(sid)+'&')
        
