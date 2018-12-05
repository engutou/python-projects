#! python

"""
使用端口不可达的udp探测包进行别名解析
Added by Zhiyong.Zhang@2018.11.28
"""
from global_config import *
from craft_packets import *


def iffinder(dst_list, dport_start=DefaultDPort, dport_constant=False, count=1, timeout=1, stiff=1):
    """
    :param dst_list: list
        目标IP地址列表

    :param dport_start: int
        第一轮udp探测包的目标端口号

    :param dport_constant: boolean
        if True, 探测包的目标端口号维持不变
        if False, 探测包的目标端口号每轮递增

    :param count: int
        尝试探测的最大次数

    :param timeout: int
        每次探测的超时门限，以秒为单位

    :param stiff: int
        0: 目标IP一旦应答，就不再探测
        1: 检测到目标IP的别名IP，就不再探测
        >=2: 每轮都对所有IP进行探测，不移除目标IP

    :return ret: dict
        以(key=目标IP，value=应答IP集合)的字典形式返回探测结果
    """
    ret = dict((dst, []) for dst in dst_list)
    c = 0
    print('Iffinder round:')
    while c < count:
        print(c + 1)
        dport_delta = 0 if dport_constant else c
        pkts = [probe_udp(dst=dst, dport=dport_start + dport_delta, count=1)[0] for dst in dst_list]
        ans, _ = sr(pkts, timeout=timeout, verbose=0)
        if len(ans) > 0:
            for r in ans.res:
                target_ip = r[0].sprintf('%IP.dst%')
                answer_ip = r[1].sprintf('%IP.src%')
                ret[target_ip].append(answer_ip)

                # 从应答报文中解析udp探测包的目标IP
                if r[1].sprintf('{ICMP:%ICMP.code%}') == 'port-unreachable' \
                        and r[1].sprintf('{ICMP:%ICMP.type%}') == 'dest-unreach':
                    target_ip2 = r[1].sprintf('{IPerror:%IPerror.dst%}')
                assert target_ip == target_ip2

                if stiff == 0:
                    # 移除已经应答的目标IP
                    dst_list.remove(target_ip)
                elif stiff == 1:
                    # 移除已经发现别名IP的目标IP
                    if target_ip != answer_ip:
                        dst_list.remove(target_ip)

        # 所有探测目标已经应答，提前结束
        if len(dst_list) == 0:
            break

        c += 1

    # 去除重复的响应IP
    for d, r in ret.items():
        ret[d] = list(set(r))
    return ret


if __name__ == "__main__":
    test = ['202.97.85.14', '202.97.37.74', '175.184.246.13', '175.184.246.19']
    test = ['171.208.203.73', '171.208.197.141']
    ret = iffinder(test, count=10, stiff=1)
    for d, r in ret.items():
        print(d, ':', r)

    # test = ['202.97.85.14']
    # ret = iffinder(test, count=20, stiff=2)
    # for d, r in ret.items():
    #     print(d, ':', r)
