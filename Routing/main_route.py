import subprocess

orbit_num, sat_num = 72, 22

src_lst = [
    '2001:266:288::/48','2001:266:288::/48',
    '2001:311:312::/48','2001:312:334::/48',
    '2001:355:356::/48','2001:356:378::/48',
    '2001:309:331::/48','2001:309:331::/48',
]
dst_lst = [
    '2001:376:398::/48','2001:397:398::/48',
    '2001:352:374::/48','2001:374:375::/48',
    '2001:483:505::/48','2001:484:505::/48',
    '2001:507:529::/48','2001:528:529::/48',
]
path_lst = [
    [266, 288, 310, 332, 354, 376, 398],[266, 288, 287, 309, 331, 353, 375, 397, 398],

    [312, 311, 310, 309, 308, 330, 352, 374],[312, 334, 356, 378, 377, 376, 375, 374],

    [356, 355, 354, 353, 352, 373, 395, 417, 439, 461, 483, 505],
    [356, 378, 400, 422, 444, 466, 488, 487, 509, 508, 507, 506, 484, 505],

    [309, 331, 353, 375, 397, 419, 441, 463, 485, 507, 529],
    [309, 331, 330, 352, 374, 396, 418, 440, 462, 484, 506, 528, 529],
]
uni_lst = [
    True,False,

    True,False,

    True,
    False,

    True,
    False
]

for src, dst, path, uni in zip(src_lst, dst_lst, path_lst, uni_lst):
    for s1, s2 in zip(path[:-1], path[1:]):
        oid1, sid1 = s1 // sat_num, s1 % sat_num
        oid2, sid2 = s2 // sat_num, s2 % sat_num
        sat1 = f'SH1O{oid1 + 1}S{sid1 + 1}'
        sat2 = f'SH1O{oid2 + 1}S{sid2 + 1}'

        if oid1 == oid2:
            if sid1 < sid2:
                if sid2 - sid1 == 1:
                    dev1, dev2 = 'eth1', 'eth2'
                else:
                    dev1, dev2 = 'eth2', 'eth1'
            elif sid1 > sid2:
                if sid1 - sid2 == 1:
                    dev1, dev2 = 'eth2', 'eth1'
                else:
                    dev1, dev2 = 'eth1', 'eth2'
            else:
                raise RuntimeError
        elif sid1 == sid2:
            if oid1 < oid2:
                if oid2 - oid1 == 1:
                    dev1, dev2 = 'eth3', 'eth4'
                else:
                    dev1, dev2 = 'eth4', 'eth3'
            elif oid1 > oid2:
                if oid1 - oid2 == 1:
                    dev1, dev2 = 'eth4', 'eth3'
                else:
                    dev1, dev2 = 'eth3', 'eth4'
            else:
                raise RuntimeError
        else:
            raise RuntimeError

        link_local1 = subprocess.check_output(f"ip netns exec {sat1} ip -6 addr show dev {dev1} | grep 'inet6 fe80'", shell=True).strip().decode()
        link_local1 = link_local1.split(' ')[1]
        link_local1 = link_local1[:link_local1.find('/')]

        link_local2 = subprocess.check_output(f"ip netns exec {sat2} ip -6 addr show dev {dev2} | grep 'inet6 fe80'", shell=True).strip().decode()
        link_local2 = link_local2.split(' ')[1]
        link_local2 = link_local2[:link_local2.find('/')]
        if uni:
            cmd = subprocess.run(('ip', 'netns', 'exec', sat2,
                'ip', '-6', 'route', 'add', src,
                'dev', dev2, 'via', link_local1,
                'metric', '10', 'pref', 'high'))
            if cmd.returncode not in (0, 2):
                print(f'Error [{cmd.returncode}]:', cmd)
                exit(1)
        cmd = subprocess.run(('ip', 'netns', 'exec', sat2,
            'ip', '-6', 'route', 'add', src,
            'dev', dev2, 'via', link_local1,
            'metric', '10', 'pref', 'high'))
        if cmd.returncode not in (0, 2):
                print(f'Error [{cmd.returncode}]:', cmd)
                exit(1)

