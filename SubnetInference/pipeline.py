# -*- coding:utf-8 -*-

import os
import ipaddress
import measure_routing_path
import build_ip_topo_graph


def predecessor_analysis(ip_graph):
    dst_net = ipaddress.IPv4Network(ip_graph.graph[build_ip_topo_graph.TraceFileHead.dst])
    reached_hosts = set([str(h) for h in dst_net.hosts()])
    reached_hosts = reached_hosts.intersection(set(ip_graph.nodes))
    print('Number of reached hosts:', len(reached_hosts))
    node2pred = {}
    for node in reached_hosts:
        node2pred[node] = set([pred for pred in ip_graph.predecessors(node)])
    return node2pred


def main():
    datadir = './Dataset/Test/'
    if False:
        measure_routing_path.main(datadir)

    # trfiles = [datadir + item for item in os.listdir(datadir) if item.endswith('.trace')]
    trfiles = [datadir + item for item in ['61.63.92.0-22.trace']]
    for trfile in trfiles:
        # 为每个trace文件处理一次
        print('Processing {0}'.format(trfile))
        stat, g = build_ip_topo_graph.main(trfile)
        if stat:
            node2pred = predecessor_analysis(ip_graph=g)


if __name__ == '__main__':
    main()