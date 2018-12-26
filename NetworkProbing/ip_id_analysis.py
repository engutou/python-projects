#! python
# -*- coding: utf-8 -*-

from scapy.all import *
import time

from craft_packets import *
from global_config import *


def ip_id_classifier(dst, proto='icmp', prb_round=5):
    """
    用指定协议探测单个目标IP的IP-ID响应策略
    :param dst: string
        单个目标IP地址
    :param proto:
    :param prb_round:
    :return:
    """
    sipid_list, ripid_list = [], []
    while prb_round > 0:
        dst2idseq = ip_id_extractor(dst, proto=proto)
        id_data_list = dst2idseq[dst] if dst in dst2idseq else []
        if len(id_data_list) == 0:
            prb_round -= 1
            continue
        id_data_list = list(zip(*id_data_list))
        sipid_list.extend(id_data_list[0])
        ripid_list.extend(id_data_list[1])

        n = len(ripid_list)
        if n >= 2:
            if sipid_list == ripid_list:
                # 用探测包的IP-ID作为响应包的IP-ID
                return n, IpIDMode.ProbVal
            if len(set(ripid_list)) == 1:
                # 用某个常数作为响应包的IP-ID
                return n, IpIDMode.Const
            else:
                # 正常情况
                return n, IpIDMode.Normal
        else:
            prb_round -= 1
    return len(ripid_list), IpIDMode.Unknown


def ip_id_extractor(dst, proto='icmp', pkt_count=2):
    """
    对一系列目标IP发送一系列探测包，抽取响应包的IP-ID
    :param dst: string or list/tuple/set of strings
        每个string都是一个IP地址
    :param proto:
        探测包协议
    :param pkt_count:
        发往每个目标IP地址的探测包数量
    :return:
    """
    if proto == 'icmp':
        pkts = probe_icmp(dst, count=pkt_count)
    elif proto == 'udp':
        pkts = probe_udp(dst, dport=DefaultDPort, count=pkt_count)
    elif proto == 'tcp':
        pkts = probe_tcp(dst, dport=80, count=pkt_count)
    else:
        print('Unknown protocol...')
        return None

    ans, _ = sr(pkts, timeout=1, verbose=0)
    dst2idseq = {}
    if len(ans) > 0:
        for r in ans.res:
            # 从报文中解析IP-ID
            d = r[0].sprintf('%IP.dst%')
            sid = r[0].sprintf('%IP.id%')
            rid = r[1].sprintf('%IP.id%')
            if d in dst2idseq:
                dst2idseq[d].append([sid, rid])
            else:
                dst2idseq[d] = [[sid, rid]]
    return dst2idseq


def ally(dst_list, proto='icmp', prb_round=1):
    dst2idseq = dict([(d, []) for d in dst_list])
    r = 1
    while r <= prb_round:
        dst2idseq_ = ip_id_extractor(dst=dst_list, proto=proto)
        for d, idseq in dst2idseq_.items():
            for item in idseq:
                item[0] = str(r) + '.' + item[0]
                item[1] = str(r) + '.' + item[1]
            dst2idseq[d].extend(idseq)
        r += 1
    for d, idseq in dst2idseq.items():
        print(d, idseq)


if __name__ == "__main__":
    test = ['192.168.1.1', '202.112.14.178', '202.97.85.14', '202.97.42.82', '202.97.37.74']
    proto_list = ['icmp', 'udp', 'tcp']

    # for d in test:
    #     for proto in proto_list:
    #         num_ans, ip_id_mode = ip_id_classifier(d, proto=proto, prb_round=5)
    #         print(d, proto, num_ans, ip_id_mode)
    #         if ip_id_mode == IpIDMode.Normal:
    #             break

    for proto in proto_list:
        print(proto)
        ally(dst_list=test, proto=proto, prb_round=10)