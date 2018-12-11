# -*- coding:utf-8 -*-

import os
import ipaddress
from collections import Counter
import measure_routing_path
import build_ip_topo_graph


def predecessor_analysis(ip_graph, verbose=0):
    """
    根据IP topology graph（IP链路构成的有向图）分析目标网络中，可达IP的前驱节点

    :param ip_graph: networkx.DiGraph
        存放IP链路信息的图结构

    :param verbose: int
        控制信息输出

    :return node2pred: dict
        key: string, reachable IP addresses in the target network
        value: set of strings, 对应节点的前驱节点集合
    """
    dst_net = ipaddress.IPv4Network(ip_graph.graph[build_ip_topo_graph.TraceFileHead.dst])
    reached_hosts = set([str(h) for h in dst_net.hosts()])
    reached_hosts = reached_hosts.intersection(set(ip_graph.nodes))
    node2pred = {}
    for node in reached_hosts:
        node2pred[node] = set([pred for pred in ip_graph.predecessors(node)])

    if verbose >= 1:
        num_preds = [len(pset) for pset in node2pred.values()]
        num_preds_to_num_nodes = Counter(num_preds)
        num_multi_pred_nodes = sum([nn for np, nn in num_preds_to_num_nodes.items() if np > 1])
        print('(num_preds, num_IPs) =', sorted(num_preds_to_num_nodes.items(), key=lambda x: x[0]))
        print('>>>> {r:2.1f}% IPs have multiple predecessors.'
              .format(r=100.0 * num_multi_pred_nodes / (num_multi_pred_nodes + num_preds_to_num_nodes[1])))

    return node2pred


def main():
    datadir = './Dataset/Test/'
    if False:
        measure_routing_path.main(datadir)

    trfiles = [datadir + item for item in os.listdir(datadir) if item.endswith('.trace')]
    for trfile in trfiles:
        # 为每个trace文件处理一次
        print('Processing \"{0}\"'.format(os.path.abspath(trfile)))
        stat, g = build_ip_topo_graph.main(trfile)
        if stat:
            node2pred = predecessor_analysis(ip_graph=g, verbose=1)



if __name__ == '__main__':
    main()