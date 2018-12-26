#! python
"""
Added by Zhiyong.Zhang@2018.11.16
利用Scapy生成各种探测报文
"""

from scapy.all import *
from random import randint
import ipaddress


def probe_icmp(dst, ttl=64, count=1):
    """
    生成icmp echo request报文

    :param dst: string or list/tuple/set of strings
        每个string都是点分十进制的IPv4地址，请求报文的目的IP

    :param ttl: int
        报文的ttl值

    :param count: int
        报文数量

    :return pkts: list of packets
    """
    is_single = not (isinstance(dst, list) or isinstance(dst, tuple) or isinstance(dst, set))
    dst = [dst] if is_single else dst

    ip_id = randint(1, 55535)
    icmp_id = randint(1, 55535)
    icmp_seq = randint(1, 55535)

    pkts = []
    for i in range(count):
        for j, d in enumerate(dst):
            id_offset = i * len(dst) + j
            pkts.append(IP(dst=d, ttl=ttl, id=ip_id + id_offset) /
                        ICMP(id=icmp_id + id_offset, seq=icmp_seq + id_offset))
    return pkts


def probe_tcp(dst, dport=80, ttl=64, count=1):
    is_single = not (isinstance(dst, list) or isinstance(dst, tuple) or isinstance(dst, set))
    dst = [dst] if is_single else dst

    ip_id = randint(1, 55535)
    pkts = []
    for i in range(count):
        for j, d in enumerate(dst):
            id_offset = i * len(dst) + j
            pkts.append(IP(dst=d, ttl=ttl, id=ip_id + id_offset) / TCP(dport=dport, flags='S'))
    return pkts


def probe_udp(dst, dport=54321, ttl=64, count=1):
    is_single = not (isinstance(dst, list) or isinstance(dst, tuple) or isinstance(dst, set))
    dst = [dst] if is_single else dst

    ip_id = randint(1, 55535)
    pkts = []
    for i in range(count):
        for j, d in enumerate(dst):
            id_offset = i * len(dst) + j
            pkts.append(IP(dst=d, ttl=ttl, id=ip_id + id_offset) / UDP(dport=dport))
    return pkts
