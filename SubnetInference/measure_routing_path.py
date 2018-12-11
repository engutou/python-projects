#! python
# -*- coding:utf-8 -*-
from random import shuffle
import ipaddress
import socket
import sys
sys.path.append('../NetworkProbing/')
sys.path.append('../Util')
import traceroute
import Util


def main(datadir, ttl=range(1, 26), repeat=1):
    subnet_list = Util.read_to_list(datadir + 'IpBlocks.txt')
    for net in subnet_list:
        if net.startswith('#'):
            continue
        print('Probing:', net)
        net = ipaddress.IPv4Network(net)
        host_list = list(net.hosts())

        count = 0
        ret_data = ['Vantage:\t' + socket.gethostbyname(socket.gethostname()),
                    'Destination:\t' + str(net),
                    'TTL:\t' + ' '.join([str(t) for t in ttl])]

        while repeat > 0:
            repeat -= 1
            shuffle(host_list)
            for dst in host_list:
                rtpath = traceroute.traceroutefast(str(dst), timeout=1, ttl=ttl, ostr=False)
                # 必须先获取EOP状态
                dst_reached = (rtpath[-1][-1] == 'EOP')
                rtpath = [item[1] for item in rtpath]
                if dst_reached:
                    # We have reached the destination
                    ret_data.append('+' + str(dst) + ':\t' + ' '.join(rtpath))
                else:
                    # We MAY have not reached the destination
                    ret_data.append('-' + str(dst) + ':\t' + ' '.join(rtpath))
                count += 1
                if count % 1e3 == 0:
                    print(count, 'IPs are probed.')

                rtpath.append('Reached the destination!' if dst_reached else 'MAY not reached the destination!')
                Util.write_list(rtpath, 'trace.tmp')

        tracefile = datadir + str(net.network_address) + '-' + str(net.prefixlen) + '.trace'
        Util.write_list(ret_data, tracefile)


if __name__ == '__main__':
    datadir = './Dataset/Test/'
    main(datadir, ttl=range(3, 16), repeat=5)
