#! python

from scapy.all import *
import time

from craft_packets import *
from global_config import *


def ping(dst, proto='icmp', dport=DefaultDPort, count=1):
    """
    普通版本的ping，即使对目标IP的探测次数>count<大于1，每次也只发送一个探测包
    :param dst: 目的IP
    :param proto: 协议类型，{icmp, tcp, udp}
    :param dport: 目的端口
    :param count: 探测次数
    :return result: string
    """
    # 一次性产生>count<个探测包
    if proto.lower() == 'icmp':
        pkts = probe_icmp(dst=dst, count=count)
    elif proto.lower() == 'tcp':
        pkts = probe_tcp(dst=dst, dport=dport, count=count)
    elif proto.lower() == 'udp':
        pkts = probe_udp(dst=dst, dport=dport, count=count)
    else:
        print('Unknown protocol...')
        return None

    result = ''
    for i in range(0, count):
        ans = sr1(pkts[i], timeout=1, verbose=0)
        if ans:
            ans_str = ans.sprintf('ttl=%IP.ttl%\tanswer_ip=%IP.src%')
            result += '%d:\t%s\n' % (i + 1, ans_str)
        else:
            result += '%d:\ttime out\n' % (i + 1)
    return result


if __name__ == "__main__":
    test = ['202.112.14.178', '202.97.85.14', '202.97.37.74']
    for d in test:
        print(ping(d, proto='icmp', count=2))
