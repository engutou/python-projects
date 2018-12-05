#! python
# -*- coding: utf-8 -*-

from util_database import *
from util_ip import *
from util_statistics import *
from util_file import *
import os
import codecs
from networkx import Graph, core_number
from string import printable
import json


#############################################
# Basic algorithms
#############################################
def dict2str(data_list, intra_sep=' ', inter_sep=', '):
    # 要求输入data_list的每个元素都可以转化为string
    if data_list:
        ret = ''
        for k, v in data_list.iteritems():
            ret += (str(k) + intra_sep + str(v) + inter_sep)
        return ret.rstrip(inter_sep)
    else:
        return None


def list2str(data_list, sep=' '):
    # 将data_list的所有元素合并为一个string，用“sep”分隔
    # 要求输入data_list的每个元素都可以转化为string
    if data_list:
        ret = ''
        for d in data_list:
            ret += (str(d) + sep)
        return ret.rstrip(sep)
    else:
        return None


def dict_list2nest_dict(dict_list, main_key):
    """
    将一个字典数组转化为嵌套的字典
    :param dict_list: [{k1: v11, k2: v21, k3: v31}, {k1: v12, k2: v22, k3: v32}, ...]
    :param main_key: 将list中各个元素的某个key提出来作为新的dict的key
    :return: dict, 假如main_key == k1，那么: {v11: {k2: v21, k3: v31}, v12: {k2: v22, k3: v32}, ...}

    warning:
    main_key必须是所有元素公共的key，而且对应值必须可用作key

    """
    ret_data = {}
    if isinstance(main_key, str):
        for item in dict_list:
            item = dict(item)
            k = item[main_key]
            item.pop(main_key)
            ret_data[k] = item
    elif isinstance(main_key, tuple):
        for item in dict_list:
            item = dict(item)
            k = []
            for t in main_key:
                k.append(item[t])
                item.pop(t)
            k = tuple(k)
            ret_data[k] = item
    else:
        print "main_key can only be a string or tuple"
    return ret_data


def nest_dict2dict_list(nest_dict, main_key):
    """
    将嵌套的字典转化为一个字典数组
    :param nest_dict: {v11: {k2: v21, k3: v31}, v12: {k2: v22, k3: v32}, ...}
    :param main_key: 嵌套字典第一层的key转化为value时分配的key
    :return: dict_list: 假如main_key == k1, 那么输出[{k1: v11, k2: v21, k3: v31}, {k1: v12, k2: v22, k3: v32}, ...]

    warning:
    main_key必须是所有元素公共的key，而且对应值必须可用作key

    """
    dict_list = []
    if isinstance(main_key, str):
        for k, v in nest_dict.iteritems():
            assert not isinstance(k, tuple)
            d = dict(v)
            d[main_key] = k
            dict_list.append(d)
    elif isinstance(main_key, tuple):
        for k, v in nest_dict.iteritems():
            assert len(k) == len(main_key)
            d = dict(v)
            for i in range(len(main_key)):
                d[main_key[i]] = k[i]
            dict_list.append(d)
    return dict_list


def merge_nest_dict(nest_dict_old, nest_dict_new):
    """
    将两个嵌套字典进行合并，如果存在重叠，则用后者覆盖前者
    :param nest_dict_old:
    :param nest_dict_new:
    :return:
    """
    ret = nest_dict_old.copy()
    for k, v in nest_dict_new.iteritems():
        if k in ret:
            ret[k] = dict(ret[k], **v)
        else:
            ret[k] = v
    return ret


def is_sub_list(l1, l2):
    # 功能：If l1 is a sublist of l2, return True; Otherwise, return False
    m, n = len(l1), len(l2)
    if m <= n:
        # l2 contains l1
        for i in range(0, n-m+1):
            if l1 == l2[i: i+m]:
                return True
    return False


def is_exclusive_intervals(intervals):
    # intervals is a list of tuples,
    # the first and second elements of each tuple are integers indicating an interval
    intersect_pairs = []
    for i in range(len(intervals)):
        i_start, i_end = intervals[i][0], intervals[i][1]
        for j in range(i+1, len(intervals)):
            j_start, j_end = intervals[j][0], intervals[j][1]
            if i_start > j_end or i_end < j_start:
                continue
            intersect_pairs.append((i, j))
    return (len(intersect_pairs) == 0), intersect_pairs


def set_to_pair_list(s, ordered=False):
    """
    将一个集合中的元素两两配对，并存放在一个list中
    :param s: 包含多个元素的list，tuple，或者set
    :return: list of tuples, each tuple contains two elements
    """
    s = list(set(s))
    ret = []
    # 将if放在for循环外面，可以提升程序运行效率 -- 减少if判断次数
    if ordered:
        for i in range(len(s)):
            for j in range(i+1, len(s)):
                ret.append((min(s[i], s[j]), max(s[i], s[j])))
    else:
        for i in range(len(s)):
            for j in range(i+1, len(s)):
                ret.append((s[i], s[j]))
    return ret


def list_split(lt, sep):
    # 功能：类似与string的split，根据sep指定的值，将输入的list或者tuple分裂为多个list
    # e.g. if sep = '*': [1, 2, 3, '*', 4, 5, 6] ==> [[1,2,3],[4,5,6]]
    # 输入：lt存放待分裂的list数据，sep表示分隔符
    # 输出：list of tuples
    lt.append(sep)
    ret = []
    i0, i = 0, 0
    while i < len(lt):
        if lt[i] == sep:
            # ret.append(tuple([lt[k] for k in range(i0, i)]))
            ret.append(tuple(lt[i0:i]))
            i0 = i + 1
        i += 1
    list_shrink(ret, keep_order=True)
    try:
        ret.remove(())
    except ValueError:
        pass
    return ret


#############################################
# 去除list数据中的冗余
#############################################
def list_shrink(data_list, keep_order=False, allow_repeat=[]):
    # 功能：对于list中多次出现的元素，仅保留第一次；allow_repeat中存放的元素可以重复
    # 输入：data_list是一个list
    # 输出：无
    if keep_order:
        known_elements = set()
        newlist = []
        for d in data_list:
            if d in known_elements:
                continue
            newlist.append(d)
            if d not in allow_repeat:
                known_elements.add(d)
        data_list[:] = newlist
    else:
        data_list[:] = list(set(data_list))


def list_element_merge(set_list, silent=True):
    """
    将set_list中存在交集的元素合并，不存在交集的元素不理会
    :param set_list: a list of iterables (e.g. list, set, tuple)
    :param silent: print debug info. or not
    :return:
    """
    # 输入：set_list是一个包含多个元素的list，其中每个元素可能是list，set，tuple等容器；
    # 输出：a list of sets
    # e.g. [(1,2), [2,2,3], {4,5}] ==> [{1,2,3}, {4,5}]
    set_list_new = []
    known_elements = set()
    cnt = 0
    for one_set in set_list:
        cnt += 1
        if cnt % 1e3 == 0 and not silent:
            print 'set_list_union(): {0}/{1} are done.'.format(cnt, len(set_list))
        # 转换输入list的每个元素为set
        one_set = set(one_set)
        if known_elements & one_set:
            # 初步判断存在交集时，才去寻找具体和谁有交集
            for i in range(len(set_list_new)):
                set_in_new = set(set_list_new[i])
                if one_set & set_in_new:
                    one_set = one_set | set_in_new
                    set_list_new[i] = None
            set_list_new = filter(None, set_list_new)
        set_list_new.append(one_set)
        known_elements = known_elements | one_set
    if not silent:
        print 'list_element_merge(): {0}/{1} are done.'.format(cnt, len(set_list))
    assert not intersect_any(set_list_new)
    return set_list_new


def list_element_union(set_list):
    """
    获得set_list中所有元素的并集, e.g. [(1,2), [2,2,3], {4,5}] ==> [1, 2, 3, 4, 5]
    :param set_list: a list of iterables
    :return: list
    """
    ret_list = []
    for item in set_list:
        ret_list.extend(list(item))
    list_shrink(ret_list, keep_order=False)
    return ret_list


def list_element_rmsub(list_list):
    # 功能：将list_list中属于其他元素子集的元素移除
    # 输入：list_list是一个包含多个元素的list，其中每个元素可能是list，tuple等容器，不可以是set；
    # e.g. [(1,2), [1,2,3], (4,5)] ==> [(1, 2, 3), (4, 5)]
    # 输出：a list of lists/tuples
    to_remove = []
    for i in range(len(list_list)):
        if i not in to_remove:
            i_remove = False
            for j in range(i + 1, len(list_list)):
                if is_sub_list(list_list[i], list_list[j]):
                    i_remove = True
                    break
                elif is_sub_list(list_list[j], list_list[i]):
                    to_remove.append(j)
            if i_remove:
                to_remove.append(i)
                break
    return [list_list[i] for i in range(len(list_list)) if i not in to_remove]


##
# Operations relevant to set
##
def get_sub_super_set(subset_list, superset_list):
    superset_id_list = [[] for i in range(len(subset_list))]
    subset_id_list = [[] for i in range(len(superset_list))]
    for i in range(len(subset_list)):
        for j in range(len(superset_list)):
            if set(superset_list[j]).issuperset(set(subset_list[i])):
                superset_id_list[i].append(j)
                subset_id_list[j].append(i)
    return superset_id_list, subset_id_list


def get_num_sub_super_set(subset_list, superset_list):
    superset_id_list, subset_id_list = get_sub_super_set(subset_list, superset_list)
    num_superset_list = [len(item) for item in superset_id_list]
    num_subset_list = [len(item) for item in subset_id_list]
    return num_superset_list, num_subset_list


def set_set_comparison(subset_list, superset_list):
    num_superset_list, num_subset_list = get_num_sub_super_set(subset_list, superset_list)
    if num_superset_list.count(0) > 0:
        print 'There exist {0} sets in set-1 that do not have superset in set-2'\
            .format(num_superset_list.count(0))
        return False
    if num_superset_list.count(0) + num_superset_list.count(1) < len(num_superset_list):
        print 'There exist {0} sets in set-1 that have multiple supersets in set-2'\
            .format(len(num_superset_list) - num_superset_list.count(0) - num_superset_list.count(1))
        return False
    if num_subset_list.count(0) + num_subset_list.count(1) < len(num_subset_list):
        print 'There exist {0} sets in set-2 that have multiple subsets in set-1'\
            .format(len(num_subset_list) - num_subset_list.count(0) - num_subset_list.count(1))
        return False
    return True


def set_comparison(s1, s2):
    s1 = set(s1)
    s2 = set(s2)
    print 'set comparison (s1 - s2, s1 & s2, s2 - s1) = ({0}, {1}, {2})'.format(len(s1 - s2), len(s2 & s1), len(s2 - s1))


def intersect_any(data_list):
    """
    Given a list of sets, if any two sets intersect, return True; otherwise, return False
    :param data_list: list of sets
    :return:
    """
    for i in range(len(data_list)):
        for j in range(i+1, len(data_list)):
            if set(data_list[i]) & set(data_list[j]):
                return True
    return False


##
# Operations relevant to file
##
def write_list(filename, data_list, mode='w'):
    # Write a list of data to a file
    # Each element occupy one line
    with open(filename, mode) as f:
        if data_list:
            f.write(data_list[0])
            for i in range(1, len(data_list)):
                # print i
                f.write('\n' + data_list[i])


def read_to_list(filename):
    data_list = []
    if not os.path.exists(filename):
        print 'The file \"{0}\" does not exist.'.format(os.path.abspath(filename))
    try:
        with codecs.open(filename, 'rb', get_encoding(filename)) as f:
            data_list = f.readlines()
    except IOError:
        print 'The file \"{0}\" is not readable.'.format(os.path.abspath(filename))
    finally:
        # it's fine if IOError occurred in which case data_list = []
        data_list = [x.encode('ascii').rstrip('\n').rstrip('\r').rstrip(' ') for x in data_list]
    return data_list


def read_to_list_list(filename, sep=' '):
    return [item.split(sep) for item in read_to_list(filename)]


def read_to_dict(filename, sep=','):
    data = {}
    data_list = read_to_list(filename)
    for item in data_list:
        values = item.split(sep)
        data[values[0]] = values[1]
    return data


def shrink_file_by_line(ifile, ofile=''):
    # Remove duplicate lines and keep the order of the remaining lines
    if not ofile:
        ofile = ifile + '.line_unique'

    try:
        with open(ifile, 'r') as f:
            lines = f.readlines()
        list_shrink(lines, keep_order=True)
        with open(ofile, 'w') as f:
            for line in lines:
                f.write(line)
        return True
    except:
        return False


def filter_file_by_line(filename, key_words, keep=True):
    # If keep == True: remain the lines that contain at least one word in 'key_words'
    # If keep == False: remain the lines that do not contain all words in 'key_words'
    key_words_str = '['
    for word in key_words:
        key_words_str += word + '-'
    key_words_str = key_words_str.rstrip('-')
    key_words_str += ']'

    ofile = filename + '_filt_' + ('' if keep else 'not_') + key_words_str
    with open(ofile, 'w') as fw:
        with open(filename, 'r') as fr:
            for line in fr:
                if keep:
                    for word in key_words:
                        if word in line:
                            fw.write(line)
                            break
                else:
                    good = True
                    for word in key_words:
                        if word in line:
                            good = False
                            break
                    if good:
                        fw.write(line)


def extract_ip_from_alias_pair(alias_pair_list):
    # Input:
    #   alias_pair_set: a list of IP pairs in the following format
    #                   ['a1.b1.c1.d1 a2.b2.c2.d2',
    #                    'w1.x1.y1.z1 w2.x2.y2.z2',
    #                    ...]
    # Output:
    #   A set of IP addresses that are present in the input data
    ipset = [ipp.split(' ') for ipp in alias_pair_list]
    ipset = zip(*ipset)
    ipset = set(ipset[0]) | set(ipset[1])
    return ipset


def join_files(in_filenames, ofile):
    # Join the files into one
    print 'Join files to', ofile
    err_files = []
    with open(ofile, 'w') as fw:
        for filename in in_filenames:
            try:
                with open(filename, 'r') as fr:
                    fw.write(fr.read())
            except IOError:
                print 'error joining', filename
                err_files.append(filename)
    print 'Completed: %d file(s) missed.' % len(err_files)
    if len(err_files) > 0:
        print 'missed files:'
        print '--------------------------------'
        for filename in err_files:
            print filename
        print '--------------------------------'


def rewrite_file(filename):
    write_list(filename, read_to_list(filename))


def decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = decode_list(item)
        elif isinstance(item, dict):
            item = decode_dict(item)
        rv.append(item)
    return rv


def decode_dict(data):
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        if isinstance(value, unicode):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = decode_list(value)
        elif isinstance(value, dict):
            value = decode_dict(value)
        rv[key] = value
    return rv


def file_write_json_array(dict_list, filename):
    with codecs.open(filename, 'w', encoding='utf8') as f:
        f.write('[')
        b = False
        for d in dict_list:
            f.write((',\n' if b else '\n') + json.dumps(d))
            b = True
        f.write('\n]')


def file_write_json_array_split(data_list, filename):
    cnt = 0
    json_size = 500000
    while True:
        cnt += 1
        idx_range = ((cnt - 1) * json_size, min(len(data_list), cnt * json_size))
        file_write_json_array(data_list[idx_range[0]:idx_range[1]],
                              filename=filename + '.part{0}'.format(cnt))
        if cnt * json_size >= len(data_list):
            break
##
# Operations relevant to trace data
##
def get_link_from_trace(trace_list, link2hop_gap, directed=False):
    """
    根据若干条traceroute路径数据（trace）提取其中的链路
    :param trace_list: list of traces, each trace is actually a list of IP addresses
    :param link2hop_gap: dictionary {(start_ip, end_ip): hop_gap}, 现有link数据
    :return link2hop_gap: dictionary {(start_ip, end_ip): hop_gap}, 新的link数据
    """
    for trace in trace_list:
        i = 0
        while i < len(trace) - 1:
            if '*' != trace[i]:
                for j in range(i + 1, len(trace)):
                    if '*' != trace[j]:
                        link = (trace[i], trace[j]) if directed else (min(trace[i], trace[j]), max(trace[i], trace[j]))
                        if link in link2hop_gap:
                            link2hop_gap[link] = min(j - i, link2hop_gap[link])
                        else:
                            link2hop_gap[link] = j - i
                        i = j
                        break
                if j == len(trace) - 1:
                    # i+1及其之后的IP都是*
                    break
            else:
                i += 1


def get_node_from_trace(trace_list, node2attr, start_path_id=0):
    """
    根据若干条traceroute路径数据（trace）提取其中的节点信息
    :param trace_list: list of traces, each trace is actually a list of IP addresses
    :param link2hop_gap: dictionary {(start_ip, end_ip): hop_gap}, 现有link数据
    :return link2hop_gap: dictionary {(start_ip, end_ip): hop_gap}, 新的link数据
    """
    for trace in trace_list:
        start_path_id += 1
        for n in trace:
            if n in node2attr:
                node2attr[n]['path_list'].append(start_path_id)
            else:
                node2attr[n] = {}
                node2attr[n]['path_list'] = [start_path_id]
    return node2attr


#############################################
# 在IP文件中生成ip到路径的字典算法
# 对于文件中的任意IP，遍历一遍所有路径，记录
# P(i) = {经过IP i 的路径，这里用路径行号来唯一表示}
#############################################
def bulid_ip2path_dic(filename):
    topo_file_list = read_to_list(filename)
    node2attr = {}
    get_node_from_trace(topo_file_list, node2attr)

    ip2trace = {}
    for k, v in node2attr.iteritems():
        ip2trace[k] = node2attr[k]['path_list']
    return ip2trace


##
# Operations relevant to print
##
def print_running_time(start_time):
    """
    输出当前时刻与输入时刻之间的时间差，以ms为单位
    :param start_time: 输入时刻
    :return: None
    """
    end_time = time.time()
    print 'It takes {0} milliseconds.'.format((end_time - start_time) * 1e3)


def print_dangerous_info(info):
    """
    以特定方式输出相关信息
    :param info: 待输出的信息
    :return: None
    """
    print '\n#####################################################'
    print '#'
    print '# Dangerous operation:'
    print '#', info
    print '#'
    print '#####################################################\n'


def print_progress_info(info):
    """
    以特定方式输出相关信息
    :param info: 待输出的信息
    :return: None
    """
    print '\n====================================================='
    print '*'
    print '*', info
    print '*'
    print '=====================================================\n'


def print_graph_info(g, detailed=False):
    """
    以特定方式输出相关信息
    :param info: 待输出的信息
    :return: None
    """
    print '\n====================================================='
    print '*'
    if detailed:
        print '------------------------'
        print 'Detailed info. of nodes:'
        c = 1
        for node in g.nodes(data=True):
            print 'n{0}'.format(c), node
            c += 1

        print '------------------------'
        print 'Detailed info. of edges:'
        c = 1
        for edge in g.edges(data=True):
            print 'e{0}'.format(c), edge
            c += 1
    print 'Num. of nodes/edges: ({0}, {1})'.format(len(g.nodes), len(g.edges))
    print '*'
    print '=====================================================\n'


def destroy(filenamelist):
    ask = False
    for filename in filenamelist:
        if os.path.exists(filename):
            ask = True
    if ask:
        result = raw_input("File exists. Continue will destroy everything. Are you sure? (y/n) ")
        if result not in ['y', 'Y']:
            # it's not ok to destroy the files
            return False
    # it's ok to destroy the files
    return True


#############################################
# graph related algorithms
#############################################
def k_core_index(edge_list):
    """
    用k-core算法计算给定图中各节点的k-index
    :param edge_list: a list of tuples, 存储图的边信息，因而决定图的结构，
                      example：
                      [(1, 2), (2, 3), (2, 4), (3, 4), (1, 3)]
                      <==>    1--2--4
                               \ | /
                                \|/
                                 3
    :return: a dictionary whose key is the node, and value is the k-index
             example:
                 k_core_index([(1, 2), (2, 3), (2, 4), (3, 4), (1, 3)])
             ==> {1: 2, 2: 2, 3: 2, 4: 2}
    """
    return core_number(Graph(edge_list))


#############################################
# MySQL related methods
#############################################
def read_mysql_table(table_name, column_name2dict_key, sql_filter=''):
    """
    读取MySQL数据表的特定字段，并存放在字典中
    :param table_name: 数据表的名字
    :param column_name2dict_key: dict with (key, value), key对应MySQL中的列名，value对应python的dict变量中的key
    :param sql_filter: 读取MySQL表时的过滤条件，"where ..."
    :return: a list of dicts, [{k: v1}, {k: v2}, {k: v3}]
    """
    column_list, dict_key_list = column_name2dict_key.keys(), column_name2dict_key.values()
    dict_list = []
    conn = connect_database()
    cursor = conn.cursor()
    try:
        sql = 'select ' + list2str(column_list, ', ') + ' from {0} '.format(table_name) + sql_filter
        cursor.execute(sql)
        sql_data = cursor.fetchall()
        for item in sql_data:
            one_dict = {}

            for i in range(len(item)):
                one_dict[dict_key_list[i]] = item[i]

            dict_list.append(one_dict)

    except MySQLdb.Error, e:
        print "Mysql Error %d: %s" % (e.args[0], e.args[1])

    cursor.close()
    conn.close()
    return dict_list


def set_intersect_analysis(A, B):
    """
    Given two sets of sets A = {ai} (1 <= i <= m) and B = {bj} (1 <= j <= n), where each ai or bj is a set,
    find how each ai intersects with each bj fast.
    :param A: dict, (key = set_id, value = members) where members are in a list
    :param B: dict, (key = set_id, value = members) where members are in a list
    :return: a pair of dicts, (key = set_id, value = a list of tuples where each tuple record which set intersects with the key and on which item)

    example:
        A = {'a1': [1, 2, 3, 4], 'a2': [5, 6, 7], 'a3': [8]}
        B = {'b1': [1, 2, 5], 'b2': [8], 'b3': [9], 'b4': [7, 3]}
        return:
            [{'a1': [('b1', 1), ('b1', 2), ('b4', 3)], 'a3': [('b2', 8)], 'a2': [('b1', 5), ('b4', 7)]},
            {'b4': [('a1', 3), ('a2', 7)], 'b1': [('a1', 1), ('a1', 2), ('a2', 5)], 'b2': [('a3', 8)]}]
    """
    # 全集
    universe = [[], []]
    # ai和bj中各个元素到ai或者bj的索引
    reverse_map = [{}, {}]
    for i in (0, 1):  # i=0对应A；i=1对应B
        D = A if i == 0 else B
        for k, v in D.iteritems():
            # v is a list
            universe[i].extend(v)
            for item in v:
                reverse_map[i][item] = k

    intersect_map = [{}, {}]
    common = set(universe[0]) & set(universe[1])
    for x in common:
        # A和B中具体哪两个集合同时包含x
        intersect_set = (reverse_map[0][x], reverse_map[1][x])

        for i in (0, 1):  # i=0对应A；i=1对应B
            j = (i+1) % 2  # 等价于 j = 0 if i == 1 else 1
            a, b = intersect_set[i], intersect_set[j]
            # 该集合首次被发现和某个集合相交
            if a not in intersect_map[i]:
                intersect_map[i][a] = []
            intersect_map[i][a].append((b, x))

    return intersect_map


#############################################
# 在IP文件中生成ip到路径的字典算法
# 对于文件中的任意IP，遍历一遍所有路径，记录
# P(i) = {经过IP i 的路径，这里用路径行号来唯一表示}
#############################################
def bulid_ip2path_dic(filename):
    ip2trace = {}
    topo_file_list = read_to_list(filename)
    j = 0
    for trace in topo_file_list:
        if ',' in trace:
            trace = trace.split(',')[-1].split()
        else:
            trace = trace.split()
        j = j + 1
        for k in range(len(trace)):
            ip = trace[k]
            if ip != '*':
                trace_number = []
                if ip in ip2trace:
                    ip2trace[ip].append(j)
                else:
                    trace_number.append(j)
                    ip2trace[ip] = trace_number
    return ip2trace


def merge_duplicate2solo_set_list(duplicate_set_list):
    """
     Given a list of sets A = [(),(),()...],
        if this exits intersect of sets, join them.
    :param duplicate_set_list: list of sets
    :return: list of sets, need to satisfy condition of assert not intersect_any(list)

    example:
        list = [ (1,2,3),(4,5,6),(3,4),(7,8),(8,9),(6,12,13) ]
        return:
            [(1,2,3,4,5,6,12,13),(7,8,9)]
    """
    solo_set_list = []
    len1 = len(duplicate_set_list)
    for i in range(len1):
        for j in range(len1):
            solo_set_list_tmp = duplicate_set_list[i] | duplicate_set_list[j]
            len2 = len(list(duplicate_set_list[j])) + len(list(duplicate_set_list[i]))
            if i == j or duplicate_set_list[i] == 0 or duplicate_set_list[j] == 0:
                break
            elif len(solo_set_list_tmp) < len2:
                duplicate_set_list[i] = solo_set_list_tmp
                duplicate_set_list[j] = set([0])
    for i in range(len1):
        if duplicate_set_list[i] != set([0]):
            solo_set_list.append(duplicate_set_list[i])
    return solo_set_list


if __name__ == '__main__':
    pass
