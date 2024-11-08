import time
import subprocess

orbit_num, sat_num = 10, 10

with open('network.txt', 'r') as f:
    dt = eval(f.read())

for idx, links in dt.items():
    for pair, link in links.items():
        oid, sid = (idx - 1) // sat_num, (idx - 1) % sat_num
        up_sid = sid + 1 if sid + 1 < sat_num else 0
        down_sid = sid - 1 if sid > 0 else sat_num - 1
        right_oid = oid + 1 if oid + 1 < orbit_num else 0
        left_oid = oid - 1 if oid > 0 else orbit_num - 1
        sat_name = f'SH1O{oid + 1}S{sid + 1}'
        name_map = {
            f'{(oid * sat_num + up_sid + 1)}:{idx}':f'SH1O{oid+1}S{up_sid+1}',
            f'{idx}:{oid * sat_num + down_sid + 1}':f'SH1O{oid+1}S{down_sid+1}',
            f'{right_oid * sat_num + sid + 1}:{idx}':f'SH1O{right_oid+1}S{sid+1}',
            f'{idx}:{left_oid * sat_num + sid + 1}':f'SH1O{left_oid+1}S{sid+1}'
        }
        dev_name = name_map[pair]
        link_local = subprocess.check_output(
            f"ip netns exec {sat_name} ip -6 addr show dev {link['eth']}"
            "| grep 'inet6 fe80'",
            shell=True
        ).strip().decode()
        link_local = link_local.split(' ')[1]
        link_local = link_local[:link_local.find('/')]
        subprocess.check_call(
            ('ip', 'netns', 'exec', sat_name,
            'ip', 'addr', 'add', 'dev', link['eth'], link['addr'] + '/64', 'scope', 'link')
        )
        # subprocess.check_call(
        #     ('ip', 'netns', 'exec', sat_name,
        #     'ip', 'addr', 'del', 'dev', link['eth'], link_local, 'scope', 'link')
        # )


