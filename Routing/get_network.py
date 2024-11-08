import math
import os
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
import subprocess

def get_interface_names(sid):
    # Run the ifconfig command
    ifconfig_result = subprocess.run(['ip','netns','exec',sid,'ifconfig'], capture_output=True, text=True)
    
    # Split the output into lines
    lines = ifconfig_result.stdout.splitlines()
    
    # Interface names are typically the first word before a ':' in ifconfig output
    interfaces = []
    for i in range(0,len(lines),10):#line in lines:
        line=lines[i]
        #if line and not line.startswith('\t') and ':' in line:
       # if line[0].isdigit():
        interface_name = line.split(':')[0]
        
        interfaces.append(interface_name)
    
    return interfaces

# Example usage

orbit_num=72
sat_num=22
constellation_size = orbit_num * sat_num
#nodes=[[266, 288, 310, 332, 354, 376, 398],[266, 288, 287, 309, 331, 353, 375, 397, 398],[312, 311, 310, 309, 308, 330, 352, 374],[312, 334, 356, 378, 377, 376, 375, 374],[356, 355, 354, 353, 352, 373, 395, 417, 439, 461, 483, 505],[356, 378, 400, 422, 444, 466, 488, 487, 509, 508, 507, 506, 484, 505]]
nodes=[1525, 1526, 1548, 1570, 8, 30, 52, 74, 96, 118, 140, 162, 184, 206, 228, 250, 272, 294, 316, 338, 360, 382, 404, 426, 448, 470, 492, 514, 536, 558, 580, 602, 624, 646, 645,614, 636, 658, 680, 702, 724, 746, 768, 790, 812, 834, 856, 878, 900, 922, 944, 966, 988, 1010, 1032, 1054, 1076, 1098, 1120, 1142, 1164, 1186, 1208, 1230, 1252, 1274, 1296, 1318, 1340, 1362, 1384,679, 680, 681, 703, 725, 747, 769, 791, 813, 835, 857, 879, 901, 923, 945, 967, 989, 1011, 1033, 1055, 1077, 1099, 1121, 1143, 1165, 1187, 1209, 1231, 1253, 1275, 1297, 1319, 1341,1415, 1416, 1394, 1372, 1350, 1328, 1306, 1284, 1262, 1240, 1218, 1196, 1174, 1152, 1130, 1108, 1086, 1064, 1042, 1020, 998, 976, 954, 932, 910, 888, 866, 844, 822, 800, 778, 756, 734, 712, 690, 668,549, 571, 593, 615, 637, 659, 681, 703, 725, 747, 769, 791, 813, 835, 857, 879, 901, 923, 945, 967, 989, 1011, 1033, 1055, 1077, 1099, 1121, 1143, 1165, 1187, 1209, 1231, 1253, 1275, 1297, 1319, 1341, 1363,637, 659, 638, 639, 640, 641, 642, 643, 644, 645]
def get_satno(idx):
    plane=idx//sat_num+1 #[1,24]
    sat_no=(idx+1)%sat_num
    sat_no=sat_num if sat_no==0 else sat_no
    return [int(plane),int(sat_no)]
network={}

#for node in [1]:
if 1:
    #for me in range(200,600):
    for me in nodes:
        if me in network:continue
        network[me]={}
        sid='SH1'
        plane,satno=get_satno(me)
        sid+='O'+str(plane)+'S'+str(satno)
        left_sat_id=me-sat_num if me-sat_num>=0 else constellation_size+me-sat_num
        right_sat_id=(me+sat_num)%constellation_size
        up_sat_id=me+1
        down_sat_id=me-1
        if down_sat_id%sat_num ==sat_num-1:
            down_sat_id=me-1+sat_num
        if up_sat_id%sat_num==0:
            up_sat_id=me+1-sat_num
        left_ipv6="2002:"+str(left_sat_id)+":"+str(me)+"::"
        right_ipv6="2002:"+str(me)+":"+str(right_sat_id)+"::"
        up_ipv6="2002:"+str(me)+":"+str(up_sat_id)+"::"
        down_ipv6="2002:"+str(down_sat_id)+":"+str(me)+"::"
        l=str(left_sat_id)+":"+str(me)
        r=str(me)+":"+str(right_sat_id)
        u=str(me)+":"+str(up_sat_id)
        d=str(down_sat_id)+":"+str(me)
        dic={}
        interface_list = get_interface_names(sid)
        for eth in interface_list:
            ipv6=None
            addr=None
            with os.popen("ip netns exec "+sid+" ifconfig "+eth+" | grep \'inet6\' | head -n 2") as f:
                line=f.readlines()

                for i in line:
                    i=i.split(' ')
                    for a in i:
                        if a[0:4]=='2002':
                            a=a.split(':')
                            ipv6=a[1]+':'+a[2]
                        if a[0:4]=='fe80':
                            addr=a[0:]
            dic[ipv6]={}
            dic[ipv6]['addr']=addr
            dic[ipv6]['eth']=eth
        network[me]=dic
#        for e in range(1,5):
#            ipv6=None
#            addr=None
#            with os.popen("ip netns exec "+sid+" ifconfig eth"+str(e)+" | grep \'inet6\' | head -n 2") as f:
#                line=f.readlines()
#                
#                for i in line:
#                    i=i.split(' ')
#                    for a in i:
#                        if a[0:4]=='2002':
#                            a=a.split(':')
#                            ipv6=a[1]+':'+a[2]
#                        if a[0:4]=='fe80':
#                            addr=a[0:]
#            dic[ipv6]={}
#            dic[ipv6]['addr']=addr
#            dic[ipv6]['eth']='eth'+str(e)
#        network[me]=dic
file=open('/root/starlink-Grid-LeastDelay/network.txt','w')
file.write(str(network))
file.close()
