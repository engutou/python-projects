#! python

import networkx as nx
import community
import networkx.algorithms.community as nxcommunity


def set_node_attributes(G, attr_name):
    """Set attribute for each vertex of graph G.
    The name of attribute is given by >attr_name<.
    :param G: graph
    :param attr_name: string
    :return: None
    """
    if attr_name == 'k-index':
        core_number = nx.core_number(G)
        nx.set_node_attributes(G, core_number, name=attr_name)
    else:
        print('Unknown attribute name:', attr_name)


def get_neighbor_edges(G, nodes_in_community, weak_neighbor=False):
    """Return the neighbor edges of a set of nodes.
    Neighbor edges of consists of two parts:
        1. edges interconnect one node in the community and one neighbor;
        2. edges interconnect two neighbors.
    :param G: networkx.Graph
            The original graph.
    :param nodes_in_community: list
            The list contains a set of nodes in the graph.
    :param weak_neighbor: Boolean
            If True, include edges between the neighbor nodes (i.e., part-2. above)
            If False, exclude edges between the neighbor nodes.
    :return:
    """
    neighbor_nodes = []
    for n in nodes_in_community:
        neighbor_nodes.extend([n for n in nx.neighbors(G, n) if n not in nodes_in_community])
    neighbor_nodes = set(neighbor_nodes)
    neighbor_edges = [e for e in G.edges(neighbor_nodes)]

    if weak_neighbor:
        # This case returns more edges than the case that weak_neighbor is False
        nodes_ = set(nodes_in_community).union(neighbor_nodes)
        neighbor_edges = list(filter(lambda e: e[0] in nodes_ and e[1] in nodes_, neighbor_edges))
    else:
        neighbor_edges = list(filter(lambda e: e[0] in nodes_in_community or e[1] in nodes_in_community, neighbor_edges))
    return neighbor_edges


def edge_modularity(G, nodes_in_community, weight):
    """ Compute the modularity based on weighted edges.
    modularity = sum_{e in community}w_e / (sum_{e in community}w_e + sum_{e' in neighbor edges}w_e')
    :param G:
    :param nodes_in_community:
    :return:
    """
    neighbor_edges = get_neighbor_edges(G, nodes_in_community=nodes_in_community)
    weight_sum_ne = sum([G[e[0]][e[1]][weight] for e in neighbor_edges])

    edges_in_community = list(G.subgraph(nodes_in_community).edges)
    weight_sum_ce = sum([G[e[0]][e[1]][weight] for e in edges_in_community])

    return float(weight_sum_ce) / (weight_sum_ce + weight_sum_ne)


def find_local_community(G, seed_node, weight, debug_log=False):
    """ Find the local community for the seed node.
    :param G:
    :param seed_node: one node of the graph G, or a list of nodes in the graph
    :return nodes_in_community: a list of nodes in the graph
            The list consists of the nodes in the community.
    :return modularity: float
            The corresponding modularity of the community.
    """
    nodes_in_community = seed_node if isinstance(seed_node, list) else [seed_node]
    modularity = edge_modularity(G, nodes_in_community=nodes_in_community, weight=weight)
    neighbor_edges = get_neighbor_edges(G, nodes_in_community=nodes_in_community)
    if debug_log:
        print('==========\nInitial community has nodes:', nodes_in_community)
        print('Neighbor edges:', neighbor_edges)
        print('Modularity = %f' % modularity)
    while neighbor_edges:
        # Compute the edge_modularity for each neighbor edge,
        # suppose the neighbor edge is added to the community
        mod_max, c_max, e_max = 0, None, None
        for e in neighbor_edges:
            # edges in the current community
            edges_in_temp_community = list(G.subgraph(nodes_in_community).edges)
            # append the candidate edge
            edges_in_temp_community.append(e)
            nodes_in_temp_community = list(G.edge_subgraph(edges_in_temp_community).nodes)
            mod_temp = edge_modularity(G, nodes_in_community=nodes_in_temp_community, weight=weight)
            if mod_temp > mod_max:
                mod_max, c_max, e_max = mod_temp, nodes_in_temp_community, e
        if mod_max > modularity:
            if debug_log:
                print('==========\nEdge', e_max, 'and node', set(e_max).difference(nodes_in_community), 'are added to the community')

            # Update the community and the corresponding neighbor edges
            nodes_in_community = c_max
            modularity = mod_max
            neighbor_edges = get_neighbor_edges(G, nodes_in_community=nodes_in_community)

            if debug_log:
                print('The community has nodes:', nodes_in_community)
                print('Modularity = %f' % mod_max)
                print('Neighbor edges:', neighbor_edges)
        else:
            break
    return nodes_in_community, modularity


def detection_algorithm(G, edge_weight):
    """
    Execute the local community detection algorithm for a weighted undirected graph G.
    The seed nodes are selected based on the k-index of the nodes.
    Return a set of community and the corresponding modularity, where each community is actually a set of nodes.
    :param G: networkx.Graph
            The weighted undirected graph.
    """
    Gc = G.copy()
    set_node_attributes(Gc, attr_name='k-index')
    seed_node2communities = {}

    from operator import itemgetter
    while Gc.number_of_nodes() > 0:
        seed_node = max(list(Gc.nodes(data='k-index')), key=itemgetter(1))[0]
        nodes_in_community, modularity = find_local_community(Gc, seed_node=seed_node, weight=edge_weight)
        seed_node2communities[seed_node] = (nodes_in_community, modularity)
        Gc.remove_nodes_from(nodes_in_community)
    return seed_node2communities


if __name__ == "__main__":
    def sample_1():
        edge_list = [
                    ('1', '2', 10),
                    ('1', '3', 10),
                    ('2', '3', 10),
                    ('2', '4', 5),
                    ('2', '5', 5),
                    ('2', '6', 2),
                    ('3', '6', 4),
                    ('3', '7', 3),
                    ('4', '5', 20),
                    ('4', '8', 1),
                    ('6', '7', 20),
                    ('6', '8', 30),
                    ('7', '8', 30)]
        G = nx.Graph()
        G.add_weighted_edges_from(edge_list, weight='call-num')
        # print(G.nodes(data=True))
        # print(G.edges(data=True))
        # print('\n*******1*********\n', find_local_community(G, seed_node=['1', '2', '3'], weight='call-num'))
        # print('\n********2********\n', find_local_community(G, seed_node='1', weight='call-num'))
        # print('\n*********3*******\n', find_local_community(G, seed_node='8', weight='call-num'))
        # print('\n**********4******\n', find_local_community(G, seed_node='6', weight='call-num'))
        # print('\n***********5*****\n', find_local_community(G, seed_node='4', weight='call-num'))

        # partition = community.best_partition(G, weight='call-num')
        # print("Louvain Modularity: ", community.modularity(partition, G))
        # print("Louvain Partition: ", partition)
        nxcommunity.

    sample_1()




