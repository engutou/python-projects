#! python
"""
Added by Zhiyong.Zhang@2018.11.16
利用Scapy生成各种探测报文
"""

from scapy.all import *
from random import randint


def probe_icmp(dst, ttl=64, count=1):
    """
    生成icmp echo request报文

    :param dst: string
        点分十进制的IPv4地址，请求报文的目的IP

    :param ttl: int
        报文的ttl值

    :param count: int
        报文数量

    :return pkts: list of packets
    """
    ip_id = [randint(1, 65535) for i in range(count)]
    icmp_id = [randint(1, 65535) for i in range(count)]
    icmp_seq = [randint(1, 65535) for i in range(count)]
    pkts = [IP(dst=dst, ttl=ttl, id=ip_id[i]) / ICMP(id=icmp_id[i], seq=icmp_seq[i])
            for i in range(count)]
    return pkts


def probe_tcp(dst, dport=80, ttl=64, count=1):
    ip_id = [randint(1, 65535) for i in range(0, count)]
    pkts = [IP(dst=dst, ttl=ttl, id=ip_id[i]) / TCP(dport=dport, flags='S')
            for i in range(count)]
    return pkts


def probe_udp(dst, dport=54321, ttl=64, count=1):
    ip_id = [randint(1, 65535) for i in range(0, count)]
    pkts = [IP(dst=dst, ttl=ttl, id=ip_id[i]) / UDP(dport=dport)
            for i in range(count)]
    return pkts
