# -*- coding:utf-8 -*-

import networkx
import ipaddress
import os.path
import sys
sys.path.append('../Util')
import Util
from enum import Enum, unique
from operator import itemgetter


@unique
class FileType(Enum):
    original = 0
    cleaned = 1


class IpTraceFileBase(object):
    def __init__(self, filename):
        self.__org_filename = os.path.abspath(filename)
        # 判断文件类型:
        # original是原始数据；
        # cleaned是预处理后的数据，但是数据格式和原始数据一致
        self.type = FileType.original
        if filename.endswith('_cln'):
            self.type = FileType.cleaned

        if self.type == FileType.original:
            self.__cln_filename = self.__org_filename + '_cln'
        elif self.type == FileType.cleaned:
            self.__cln_filename = self.__org_filename

        self.version = -1

    def org_filename(self):
        return self.__org_filename

    def cln_filename(self):
        return self.__cln_filename

    # def olt_filename(self):
    #     return self.__olt_filename

    @staticmethod
    def __vprint__(verbose):
        if verbose:
            return print
        else:
            return lambda x: None

    @staticmethod
    def is_valid_trace(rtpath, verbose=False):
        """
        判断traceroute探测得到的一条路由路径是否正确

        :param rtpath: list
            routing path, IP地址列表

        :param verbose: boolean
            控制信息输出
            False：不输出辅助信息；True: 输出辅助信息

        :return ret: boolean
            True
        """
        vprint = IpTraceFileBase.__vprint__(verbose)
        # 该路径至少包含两个IP地址
        if len(rtpath) > 1:
            # 判断每个非匿名IP是否只出现一次
            ip_non_anonymous_list = list(filter(lambda x: x != '*', rtpath))
            if len(ip_non_anonymous_list) < 2:
                vprint('Invalid: A valid routing path must contain at least two non-anonymous IPs.')
                return False

            if len(ip_non_anonymous_list) == len(set(ip_non_anonymous_list)):
                # 没有重复出现的IP地址，也就是没有路由环路
                for i in range(len(rtpath) - 1):
                    if rtpath[i] != '*' and rtpath[i + 1] != '*':
                        # 存在连续两个非匿名IP地址，该路径包含至少一条链路，于是valid
                        return True
            else:
                vprint('Invalid: A valid routing path cannot have routing loops.')
        else:
            vprint('Invalid: A valid routing path must contain at least two hops.')

        return False

    @staticmethod
    def extract_links(rtpath, rtts=None):
        """
        根据一条路由路径抽取IP链路
            e.g. (x.x.x.a -> x.x.x.b) => 返回{(x.x.x.a, x.x.x.b): (1,)}
                 (x.x.x.a -> * -> x.x.x.b) => 返回{(x.x.x.a, x.x.x.b): (2,)}

        :param rtpath: list
            list of IPs

        :return link_list: dict
        """
        link2data = {}
        i = 0
        while i < len(rtpath) - 1:
            if rtpath[i] == '*':
                i += 1
                continue

            for j in range(i + 1, len(rtpath)):
                if rtpath[j] != '*':
                    if rtts:
                        link2data[(rtpath[i], rtpath[j])] = [(j - i, max(0.0, float(rtts[j]) - float(rtts[i])))]
                    else:
                        link2data[(rtpath[i], rtpath[j])] = [(j - i,)]
                    i = j
                    break
        return link2data

    @staticmethod
    def clean_link_data(link2data):
        for link, data in link2data.items():
            min_length = min(data, key=itemgetter(0))[0]
            link2data[link] = list(filter(lambda x: x[0] == min_length, data))


class IpTraceFileV1(IpTraceFileBase):
    pass


class IpTraceFileV2(IpTraceFileBase):
    """
    This is an example of a trace file
        # TOOL:NMAP
        # PRO:UDP
        # TIME:2018-05-24 15:04:08
        # DST,VantagePoint,HOP:MS......
        117.194.201.244,10.42.0.224,*:* 110.185.170.129:2.85 220.166.252.137:3.45 ...
        59.96.18.137,10.42.0.224,10.42.0.1:0.16 110.185.170.129:1.15 125.69.64.213:2.28 ...
        ...
    """
    def __init__(self, filename):
        IpTraceFileBase.__init__(self, filename)
        self.version = 2
        self.head_line_length = 4

    def clean_trace_data(self, lazy=True):
        """
        预处理traceroute探测得到的原始数据文件
            1. 将非法IP（比如私有IP）替换为匿名IP（用*表示）
            2. 将末尾的匿名IP删除：(a, b, c, d, *, *, *, *) => (a, b, c, d)
            3. 判断路径是否正常，若异常，直接删除该路径

        :param lazy: boolean
            True: 如果返回文件已经存在，直接跳过，不重新处理
            False: 不论返回文件是否已经存在，都重新处理一遍

        :return: int
            -1: 执行异常
            0: 不必做任何操作
            1: 正常执行
        """
        if self.type != FileType.original:
            return -1

        if lazy and os.path.exists(self.cln_filename()):
            return 0

        lines = Util.read_to_list(self.org_filename())
        if not lines:
            return -1

        for i in range(self.head_line_length, len(lines)):
            # example:
            #   117.194.201.244,10.42.0.224,*:* 110.185.170.129:2.85 220.166.252.137:3.45 ...
            items = lines[i].split(',')
            trace = items[-1].split(' ')
            trace = [hop.split(':') for hop in trace]
            trace = list(zip(*trace))
            rtpath, rtts = list(trace[0]), list(trace[1])

            # 1. 替换非法IP
            rtpath = [h if h != '*' and ipaddress.IPv4Address(h).is_global else '*' for h in rtpath]
            rtts = [rtts[i] if h != '*' else '*' for i, h in enumerate(rtpath)]

            # 2. 移除末尾的匿名IP
            for h in range(1, len(rtpath) + 1):
                if rtpath[len(rtpath) - h] != '*':
                    break
            rtpath = rtpath[:len(rtpath) - h + 1]
            rtts = rtts[:len(rtts) - h + 1]

            # 3. 判断是否正常路径
            if self.is_valid_trace(rtpath):
                trace = [rtpath[i] + ':' + rtts[i] for i in range(len(rtpath))]
                items[-1] = ' '.join(trace)
                lines[i] = ','.join(items)
            else:
                lines[i] = None
        # 移除异常路径
        lines = list(filter(None, lines))
        print('Generate cleaned trace file \"{0}\"'.format(os.path.abspath(self.cln_filename())))
        Util.write_list(lines, self.cln_filename())
        return 1

    def extract_trace_data(self):
        """
        根据traceroute探测得到的数据文件抽取IP链路

        :return link_set: dict
            key = (source_node, target_node)
            value = list of link data, each entry is a tuple: (link_length, link_latency)
        """
        if self.type == FileType.original:
            stat = self.clean_trace_data(lazy=True)
            if stat == -1:
                return {}

        lines = Util.read_to_list(self.cln_filename())
        if not lines:
            return {}

        # 读取文件头部信息
        pass

        # 抽取链路信息
        link_set = {}
        for i in range(self.head_line_length, len(lines)):
            # example:
            #   117.194.201.244,10.42.0.224,*:* 110.185.170.129:2.85 220.166.252.137:3.45 ...
            items = lines[i].split(',')
            trace = items[-1].split(' ')
            trace = [hop.split(':') for hop in trace]
            trace = list(zip(*trace))
            rtpath, rtts = list(trace[0]), list(trace[1])
            link2data = self.extract_links(rtpath, rtts)
            for link, data in link2data.items():
                if link in link_set:
                    link_set[link].extend(data)
                else:
                    link_set[link] = data
        self.clean_link_data(link_set)
        return link_set


class IpTraceFileV3(IpTraceFileBase):
    pass


if "__main__" == __name__:
    # filename = '../link_172.16.117.37_ph.csv'
    # tf = IpTraceFileV2(filename)
    # tf.extract_trace_data()

    # todo: merge multiple files
    pass
