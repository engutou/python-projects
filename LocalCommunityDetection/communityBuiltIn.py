#! python

import community  # --> http://perso.crans.org/aynaud/communities/
# import fastcommunity as fg  # --> https://networkx.lanl.gov/trac/ticket/245
import networkx as nx

g = nx.karate_club_graph()

partition = community.best_partition(g)
print("Louvain Modularity: ", community.modularity(partition, g))
print("Louvain Partition: ", partition)

G = nx.erdos_renyi_graph(100, 0.01)
partition = community.best_partition(G)
print("Louvain Modularity: ", community.modularity(partition, g))
print("Louvain Partition: ", partition)

# cl = fg.communityStructureNewman(g)
# print("Fastgreed Modularity: ", cl[0])
# print("Fastgreed Partition: ", cl[1])