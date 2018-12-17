# -*- coding: utf-8 -*-

import networkx as nx


def __remove_nontrivial_stubs__(G, anchors):
    """
    # 移除所有节点度都大于1的stub
    # 比如：下图中是s，a，b
    #         n
    #         |
    #         s
    #        / \
    #       a — b
    :param G: networx.Graph / subGraph
        连通图或者子图
    :param anchors: 锚节点
    :return nodes_to_remove: 可以被移除的节点
    """
    nodes_to_remove = []

    if len(anchors) <= 1:
        nodes_to_remove = set(G.nodes).difference(anchors)
        # 除了锚节点，其他节点都可以删除
        return nodes_to_remove

    for n in G.nodes:
        if n in anchors or n in nodes_to_remove:
            continue

        anchor2min_cut = {}
        anchors_introduce_multi_node_cut = []
        for a in anchors:
            min_cut = nx.minimum_node_cut(G, a, n)
            anchor2min_cut[a] = min_cut if min_cut else {a}

            if len(anchor2min_cut[a]) >= 2:
                anchors_introduce_multi_node_cut.append(a)
                if len(anchors_introduce_multi_node_cut) >= 2:
                    # 不能删除这个节点
                    break

        if len(anchors_introduce_multi_node_cut) >= 2:
            # 不能删除这个节点
            continue

        if len(anchors_introduce_multi_node_cut) == 0:
            # 所有锚节点到目标节点的min_cut都只包含一个元素
            min_cuts = {tuple(min_cut) for min_cut in anchor2min_cut.values()}
            if len(min_cuts) == 1:
                # todo 可以删除该节点以及该节点与min_cuts[0]中那个元素之间的所有节点
                nodes_to_remove.append(n)

        else:
            # 只有一个锚节点>am<到目标节点的min_cut包含多个元素
            am = anchors_introduce_multi_node_cut[0]
            cut_list = [cut == {am} for a, cut in anchor2min_cut.items() if a != am]
            if all(cut_list):
                # todo 可以删除该节点以及该节点与am之间的所有节点
                nodes_to_remove.append(n)
    # 返回可移除的节点
    return nodes_to_remove


def remove_stubs(G, anchors):
    """
    给定一个无向图以及一系列节点（锚节点），移除对连通这些锚节点没有贡献的节点（stub）
    :param G:
    :param anchors:
    :return:
    """
    # 判断是否所有锚节点都在图中
    for i, an in enumerate(anchors):
        if an not in G.nodes:
            print(an, 'is ignored as it\'s not in the graph.')
            del anchors[i]
    if len(anchors) <= 1:
        print('You must provide at least two anchors.')
        return False

    anchors = set(anchors)

    # 移除不包含锚节点的连通分量
    nodes_to_remove = []
    for c in nx.connected_components(G):
        # type(c) = set, a set of nodes
        if not anchors.intersection(c):
            nodes_to_remove.extend(list(c))
            print(len(c), 'nodes will be removed -- I')
    G.remove_nodes_from(nodes_to_remove)

    # 递归地移除度为1的非锚节点（非锚叶节点）
    while True:
        leaves = {n for n in G.nodes if len(G[n]) <= 1}
        leaves.difference_update(anchors)

        if len(leaves) == 0:
            break

        G.remove_nodes_from(leaves)

    # 移除所有节点度都大于1的stub
    # 比如：下图中是s，a，b
    #         n
    #         |
    #         s
    #        / \
    #       a — b
    nodes_to_remove = []
    for c in nx.connected_components(G):
        connected_subgraph = G.subgraph(c)
        sub_anchors = anchors.intersection(connected_subgraph.nodes)
        _nodes_to_remove = __remove_nontrivial_stubs__(connected_subgraph, sub_anchors)
        nodes_to_remove.extend(_nodes_to_remove)
    G.remove_nodes_from(nodes_to_remove)

    # 全部操作正常执行，返回True
    return True


if __name__ == '__main__':
    edges = [(0, 1),
             (0, 4),
             (0, 7),
             (1, 5),
             (1, 10),
             (1, 13),
             (2, 4),
             (2, 5),
             (2, 6),
             (4, 6),
             (3, 6),
             (5, 15),
             (5, 16),
             (7, 8),
             (7, 9),
             (8, 9),
             (10, 11),
             (11, 12),
             (12, 13),
             (12, 14),
             (14, 21),
             (14, 23),
             (16, 17),
             (16, 18),
             (17, 18),
             (19, 20),
             (20, 26),
             (21, 22),
             (23, 24),
             (23, 25),
             (24, 25),
             ]
    edges = {e for e in edges}
    G = nx.Graph()
    G.add_edges_from(edges)
    remove_stubs(G, anchors=[0, 1, 2, 3, 20, 1000])
    print(len(G))
