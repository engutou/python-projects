#! python

from random import shuffle
import ipaddress
import sys
sys.path.append('../NetworkProbing/')
sys.path.append('../Util')
import traceroute
import Util


def main(datadir):
    subnet_list = Util.read_to_list(datadir + 'IpBlocks.txt')
    for net in subnet_list:
        print('Probing:', net)
        net = ipaddress.IPv4Network(net)
        host_lists = [item for item in net.hosts()]
        shuffle(host_lists)

        count = 0
        ret_data = ['src:\t' + '10.42.0.169']
        for dst in host_lists:
            rtpath = traceroute.traceroutefast(str(dst), timeout=1, ttl=range(1, 26), ostr=False)
            rtpath = [item[1] for item in rtpath]
            ret_data.append(str(dst) + ':\t' + Util.list_to_str(rtpath))
            count += 1
            if count % 1e3 == 0:
                print(count, 'IPs are probed.')
            Util.write_list(rtpath, 'trace.tmp')

        tracefile = datadir + str(net.network_address) + '-' + str(net.prefixlen) + '.trace'
        Util.write_list(ret_data, tracefile)


if __name__ == '__main__':
    datadir = './Dataset/AS109/'
    main(datadir)
