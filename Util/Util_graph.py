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
    # G = nx.Graph()
    nodes_to_remove = []

    if len(anchors) <= 1:
        # 除了锚节点，其他节点都可以删除
        nodes_to_remove = set(G.nodes).difference(anchors)
        return nodes_to_remove

    for n in G.nodes:
        if n in anchors or n in nodes_to_remove:
            continue

        exist_multi_cut = False
        for a in anchors:
            # 对于每个节点n，最多寻找两次minimum_node_cut即可判断该节点是否可被删除
            min_cut = nx.minimum_node_cut(G, a, n)
            if not min_cut:
                min_cut = {a}

            if len(min_cut) == 1:
                # 假设移除min_cut，判断节点>n<所在的连通分量中是否存在锚节点
                edges_to_add_back = list(G.edges(nbunch=min_cut))
                G.remove_nodes_from(min_cut)
                for cc in nx.connected_components(G):
                    if n in cc and (not cc.intersection(anchors)):
                        # >n<所在的连通分量>cc<不再包含锚节点，可以删除整个连通分量>cc<
                        nodes_to_remove.extend(cc)
                        break
                G.add_edges_from(edges_to_add_back)
                break
            elif exist_multi_cut:
                break  # 不可删除节点>n<
            else:
                exist_multi_cut = True
    # 返回可移除的节点
    return nodes_to_remove


def remove_stubs(G, anchors):
    """
    给定一个无向图以及一系列节点（锚节点），移除对连通这些锚节点没有贡献的节点（stub）
    :param G:
    :param anchors:
    :return:
    """
    nodes_to_remove = []
    # 判断是否所有锚节点都在图中
    for i, an in enumerate(anchors):
        if an not in G.nodes:
            print(an, 'is ignored as it\'s not in the graph.')
            del anchors[i]
    if len(anchors) <= 1:
        nodes_to_remove = set(G.nodes).difference(anchors)
        G.remove_nodes_from(nodes_to_remove)

    anchors = set(anchors)

    # 移除不包含锚节点的连通分量
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
        dummy_graph = nx.Graph(connected_subgraph.edges)

        _nodes_to_remove = __remove_nontrivial_stubs__(dummy_graph, sub_anchors)
        nodes_to_remove.extend(_nodes_to_remove)

    G.remove_nodes_from(nodes_to_remove)


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
             (3, 6),
             (4, 6),
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
    print(sorted(list(G.nodes)))
