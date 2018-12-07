#! python
# -*- coding:utf-8 -*-

import networkx
import ipaddress
import os.path
import sys
sys.path.append('../Util')
import Util


# from collections import namedtuple
# TraceFileHeadTemplate = namedtuple(typename='TraceFileHeadTemplate',
#                                    field_names=['vantage'])
TraceFileHead = ('Vantage',)


def is_valid_trace(rtpath, verbose=0):
    """
    判断traceroute探测得到的一条路由路径是否正确

    :param rtpath: list
        routing path, IP地址列表

    :param verbose: int
        控制信息输出，0：不输出；值越大，输出的信息越详细

    :return ret: boolean
        True
    """
    # 该路径至少包含两个IP地址
    if len(rtpath) > 1:
        # 判断每个非匿名IP是否只出现一次
        ip_non_anonymous_list = list(filter(lambda x: x != '*', rtpath))
        if len(ip_non_anonymous_list) < 2:
            if verbose >= 1:
                print('Invalid: A valid routing path must contain at least two non-anonymous IPs.')
            return False

        if len(ip_non_anonymous_list) == len(set(ip_non_anonymous_list)):
            # 没有重复出现的IP地址，也就是没有路由环路
            for i in range(len(rtpath)-1):
                if rtpath[i] != '*' and rtpath[i+1] != '*':
                    # 存在连续两个非匿名IP地址，该路径包含至少一条链路，于是valid
                    return True
        else:
            if verbose >= 1:
                print('Invalid: A valid routing path cannot have routing loops.')
    else:
        if verbose >= 1:
            print('Invalid: A valid routing path must contain at least two hops.')

    return False


def extract_head(file_head):
    """
    根据traceroute探测数据文件抽取头部信息

    :param file_head: list of strings

    :return:
    """
    trace_head = {}
    for line in file_head:
        items = line.split('\t')
        key, value = items[0].rstrip(':'), items[1]
        if key in TraceFileHead:
            trace_head[key] = value
        else:
            print('TraceFileHead is not consistent with the file.')
            return None
    return trace_head


def extract_links(rtpath):
    """
    根据一条路由路径抽取IP链路
        e.g. (x.x.x.a -> x.x.x.b) => 返回(x.x.x.a, x.x.x.b, 1)
             (x.x.x.a -> * -> x.x.x.b) => 返回(x.x.x.a, x.x.x.b, 2)

    :param rtpath: list
        list of IPs

    :return link_list: list of 3-elements tuples
        IP链路
    """
    link_list = []
    i = 0
    while i < len(rtpath)-1:
        if rtpath[i] == '*':
            i += 1
            continue

        for j in range(i+1, len(rtpath)):
            if rtpath[j] != '*':
                link_list.append((rtpath[i], rtpath[j], j-i))
                i = j
                break
    return link_list


def clean_trace_data(trfile, lazy=True):
    """
    预处理traceroute探测得到的原始数据文件
        1. 将非法IP（比如私有IP）替换为匿名IP（用*表示）
        2. 将末尾的匿名IP删除：(a, b, c, d, *, *, *, *) => (a, b, c, d)
        3. 判断路径是否正常，若异常，直接删除该路径


    :param trfile: string
        原始数据文件的完整路径

    :param lazy: boolean
        True: 如果返回文件已经存在，直接跳过，不重新处理
        False: 不论返回文件是否已经存在，都重新处理一遍

    :return OK: boolean
        True: 操作成功
        False: 操作失败

    :return clnfile: string
        存放traceroute探测数据的完整路径
    """
    OK = True
    clnfile = trfile + '_cln'
    if lazy and os.path.exists(clnfile):
        return OK, clnfile

    lines = Util.read_to_list(trfile)

    # 读取文件头部信息
    trace_head = extract_head(lines[:len(TraceFileHead)])
    if not trace_head:
        return (not OK), None

    for i in range(len(TraceFileHead), len(lines)):
        # example: "12.5.186.244:\t182.150.24.1 * 171.208.203.101 202.97.65.201 * 202.97.94.98"
        # "\t"前面是目标IP，后面是路由路径
        items = lines[i].split('\t')
        rtpath = items[1].split(' ')

        # 1. 替换非法IP
        rtpath = [h if h != '*' and ipaddress.IPv4Address(h).is_global else '*' for h in rtpath]

        # 2. 移除末尾的匿名IP
        for h in range(1, len(rtpath)+1):
            if rtpath[len(rtpath) - h] != '*':
                break
        rtpath = rtpath[:len(rtpath) - h+1]

        # 3. 判断是否正常路径
        if not is_valid_trace(rtpath):
            lines[i] = None
        else:
            lines[i] = items[0] + '\t' + ' '.join(rtpath)
    # 移除异常路径
    lines = list(filter(None, lines))
    Util.write_list(lines, clnfile)
    return OK, clnfile


def load_trace_file(trfile, consecutive=True):
    """
    根据traceroute探测得到的数据文件抽取IP链路

    :param trfile: string
        存放traceroute探测数据的完整路径

    :param consecutive: boolean
        True: 只返回直接相连的IP地址形成的链路
              e.g. (x.x.x.a -> x.x.x.b) => 返回(x.x.x.a, x.x.x.b)
        False: 返回所有IP链路
              e.g. (x.x.x.a -> x.x.x.b) => 返回(x.x.x.a, x.x.x.b, 1)
                   (x.x.x.a -> * -> x.x.x.b) => 返回(x.x.x.a, x.x.x.b, 2)

    :return link_set: list of 2/3-elements tuples
        IP链路数据
    """
    OK = True
    lines = Util.read_to_list(trfile)

    # 读取文件头部信息
    trace_head = extract_head(lines[:len(TraceFileHead)])
    if not trace_head:
        return (not OK), None, None

    # 抽取链路信息
    link_set = []
    for i in range(len(TraceFileHead), len(lines)):
        # example: "12.5.186.244:\t182.150.24.1 * 171.208.203.101 202.97.65.201 * 202.97.94.98"
        # "\t"前面是目标IP，后面是路由路径
        items = lines[i].split('\t')
        rtpath = items[1].split(' ')
        link_list = extract_links(rtpath)
        link_set.extend(link_list)

    link_set = set(link_set)
    if consecutive:
        link_set = set(filter(lambda x: x[2] == 1, link_set))
        link_set = set(item[:2] for item in link_set)
    else:
        # todo, 处理匿名路由器
        pass
    return OK, trace_head, link_set


def build_topo_graph(trace_head, link_set):
    g = networkx.DiGraph()
    g.graph = trace_head
    g.add_edges_from(link_set)
    return g


def main(filename):
    stat, clnfile = clean_trace_data(trfile=filename)
    if stat:
        stat, trace_head, link_set = load_trace_file(trfile=clnfile)
        g = build_topo_graph(trace_head, link_set)
        return stat, g
    return stat, None


if "__main__" == __name__:
    filename = 'D:\\python-projects\\SubnetInference\\Dataset\\AS109\\12.5.186.0-23.trace'
    main(filename)
