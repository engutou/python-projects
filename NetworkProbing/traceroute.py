#! python

from scapy.all import *
import time

from craft_packets import *
from global_config import *


def dst_reached(pkt, dst):
    """
    判断探测包是否抵达目的IP
        三种判断准则：
            1. 响应报文的源IP为探测目标IP
            2. 响应报文类型为ICMP.echo-reply
            3. 响应报文类型为ICMP.dest-unreach + ICMP.port-unreachable
    :param pkt: 探测源收到的响应报文
    :param dst: 探测目标的IP地址
    :return:
    """
    if pkt.sprintf('%IP.src%') == dst \
            or pkt.sprintf('{ICMP:%ICMP.type%}') in ['echo-reply'] \
            or (pkt.sprintf('{ICMP:%ICMP.type%}') == 'dest-unreach' and
                pkt.sprintf('{ICMP:%ICMP.code%}') == 'port-unreachable'):
        return True
    return False


def print_rtpath(rtpath):
    for h in rtpath:
        s = 'ttl=%d\t%s' % (h[0], h[1])
        if len(h) == 3:
            s += '\t' + h[2]
        print(s)


def traceroute(dst, proto='icmp', dport=DefaultDPort, ttl=range(1, 31), timeout=1, ostr=True):
    if proto.lower() == 'icmp':
        pkts = [probe_icmp(dst=dst, ttl=t)[0] for t in ttl]
    elif proto.lower() == 'tcp':
        pkts = [probe_tcp(dst=dst, dport=dport, ttl=t)[0] for t in ttl]
    elif proto.lower() == 'udp':
        pkts = [probe_tcp(dst=dst, dport=dport, ttl=t)[0] for t in ttl]
    else:
        print('Unknown protocol...')
        return None

    rtpath = []  # route path
    for i in range(len(ttl)):
        ans = sr1(pkts[i], timeout=timeout, verbose=0)
        if ans:
            if not dst_reached(ans, dst):
                rtpath.append((ttl[i], ans.sprintf('%IP.src%')))
            else:
                rtpath.append((ttl[i], ans.sprintf('%IP.src%'), 'EOP'))  # End Of Path
                break
        else:
            rtpath.append((ttl[i], '*'))

    if ostr:
        print('Traceroute %s using %s:' % (dst, proto))
        print_rtpath(rtpath)
    return rtpath


def traceroutefast(dst, proto='icmp', dport=DefaultDPort, ttl=range(1, 31), timeout=1, ostr=True):
    if proto.lower() == 'icmp':
        pkts = [probe_icmp(dst=dst, ttl=t)[0] for t in ttl]
    else:
        if proto.lower() == 'tcp':
            print('Fast traceroute with tcp is not supported now...')
        elif proto.lower() == 'udp':
            print('Fast traceroute with udp is not supported now...')
        else:
            print('Unknown protocol...')
        return None

    rtpath = [None] * len(ttl)
    firstEOP = len(ttl)

    ans, _ = sr(pkts, timeout=timeout, verbose=0)
    if len(ans) > 0:
        for r in ans.res:
            t = int(r[0].sprintf('%IP.ttl%'))
            # 注意，返回的ICMP.time-exceed报文的payload里面，ttl永远等于1
            # t2 = int(r[1].sprintf('{IPerror:%IPerror.ttl%}'))
            # if t != t2:
            #     print(r[0], r[1])
            if not dst_reached(r[1], dst):
                rtpath[ttl.index(t)] = (t, r[1].sprintf('%IP.src%'))
            else:
                rtpath[ttl.index(t)] = (t, r[1].sprintf('%IP.src%'), 'EOP')
                firstEOP = min(firstEOP, ttl.index(t))

    # 处理匿名路由器
    unans = [i for i, v in enumerate(rtpath) if not v]
    for i in unans:
        rtpath[i] = (ttl[i], '*')

    # 去除最后一跳的重复数据
    if firstEOP < len(ttl) - 1:
        rtpath = rtpath[0:firstEOP + 1]

    if ostr:
        print('Fast traceroute %s using %s:' % (dst, proto))
        print_rtpath(rtpath)
    return rtpath


if __name__ == "__main__":
    test = ['202.112.14.178', '202.97.85.14', '202.97.37.74']
    test = ['202.112.14.178']
    for d in test:
        # rtpath = traceroute(d, proto='icmp', ttl=range(1, 21))
        # print(rtpath)
        rtpath = traceroutefast(d, timeout=2, ttl=range(1, 21))
        print(rtpath)

