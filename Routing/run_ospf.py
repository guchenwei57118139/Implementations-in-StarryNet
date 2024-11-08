import os,signal
import subprocess

orbit_num, sat_num = 72, 22

def process():
    #for line in os.popen("ip netns exec "+me+" ps ax | grep python3 | grep -v grep"):
    for line in os.popen("ps ax | grep bird | grep -v grep"):
        fields = line.split()

        # extracting Process ID from the output
        pid = fields[0]

        # terminating process
        os.kill(int(pid), signal.SIGKILL)
process()


path_lst = [
    [266, 288, 310, 332, 354, 376, 398],[266, 288, 287, 309, 331, 353, 375, 397, 398],

    [312, 311, 310, 309, 308, 330, 352, 374],[312, 334, 356, 378, 377, 376, 375, 374],

    [356, 355, 354, 353, 352, 373, 395, 417, 439, 461, 483, 505],
    [356, 378, 400, 422, 444, 466, 488, 487, 509, 508, 507, 506, 484, 505,399,421,443,465],

    [309, 331, 353, 375, 397, 419, 441, 463, 485, 507, 529],
    [309, 331, 330, 352, 374, 396, 418, 440, 462, 484, 506, 528, 529],
    
    [286,285,307,329,351,527]


    
]

dir = '/root/starlink-Grid-LeastDelay'

with open(dir + '/0_550-53-72-22-1/container_pid.txt', 'r') as f:
    pid_mat = [
        [pid for pid in line.strip().split(' ')]
        for line in f if len(line) > 0 and not line.isspace()
    ]

node_set = set(node for path in path_lst for node in path)

for node in node_set:
    oid, sid = node // sat_num, node % sat_num
    os.system(f'nsenter -a -t {pid_mat[sid][oid]} hostname')
    bird_ctl_path = dir + '/bird.ctl'
    subprocess.check_call(
        ('nsenter', '-a', '-t', pid_mat[sid][oid],
        'bird', '-c', dir + '/bird.conf', '-s', dir + '/bird.ctl')
    )
