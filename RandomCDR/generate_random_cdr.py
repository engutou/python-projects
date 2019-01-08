#! python

from collections import namedtuple
import numpy as np
import networkx as nx
import datetime, time
import json

CDRTemplate = namedtuple('CDRType',
                     field_names=['Calling_Number',
                                  'Called_Number',
                                  'Call_Time',
                                  'Call_Type',
                                  'CDR_Type',
                                  'Duration_SEC',
                                  'Calling_IMEI',
                                  'Called_IMEI',
                                  'Calling_IMSI',
                                  'Called_IMSI',
                                  'Calling_Latitude',
                                  'Calling_Longitude',
                                  'Called_Latitude',
                                  'Called_Longitude',
                                  'isp_name'
                                  ])
CDR = CDRTemplate(Calling_Number='Calling_Number',
                  Called_Number='Called_Number',
                  Call_Time='Call_Time',
                  Call_Type='Call_Type',
                  CDR_Type='CDR_Type',
                  Duration_SEC='Duration_SEC',
                  Calling_IMEI='Calling_IMEI',
                  Called_IMEI='Called_IMEI',
                  Calling_IMSI='Calling_IMSI',
                  Called_IMSI='Called_IMSI',
                  Calling_Latitude='Calling_Latitude',
                  Calling_Longitude='Calling_Longitude',
                  Called_Latitude='Called_Latitude',
                  Called_Longitude='Called_Longitude',
                  isp_name='isp_name')


def init_one_cdr():
    return dict((field, None) for field in CDR)


def init_cdr_graph():
    G = nx.random_regular_graph(d=5, n=1000)
    print(nx.info(G))
    # 随机生成边的权重num_calls，表示两个节点的通话次数
    edges = list(G.edges())
    num_calls = np.random.randint(1, 21, len(edges))
    edge_to_num_calls = dict((edges[i], int(num_calls[i])) for i in range(len(edges)))
    nx.set_edge_attributes(G, edge_to_num_calls, name='num_calls')
    # 随机生成节点的IMEI和IMSI号
    nodes = list(G.nodes())
    for type in ('IMEI', 'IMSI'):
        data = np.random.randint(1, 65535, len(nodes))
        node_to_data = dict((nodes[i], int(data[i])) for i in range(len(nodes)))
        nx.set_node_attributes(G, node_to_data, name=type)
    return G


def generate_cdr_data(G):
    cdr_list = []
    for e in G.edges(data='num_calls'):
        num_calls = e[-1]
        i = 0
        now = time.time()
        while i < num_calls:
            c = init_one_cdr()
            c[CDR.Calling_Number] = str(e[0])
            c[CDR.Called_Number] = str(e[1])
            c[CDR.Call_Time] = datetime.datetime.fromtimestamp(now + i * np.random.randint(5000, 10000))
            c[CDR.Call_Type] = 'voice'
            c[CDR.CDR_Type] = '0'
            c[CDR.Duration_SEC] = int(np.random.randint(1, 100))
            c[CDR.Calling_IMEI] = G.node[e[0]]['IMEI']
            c[CDR.Called_IMEI] = G.node[e[1]]['IMEI']
            c[CDR.Calling_IMSI] = G.node[e[0]]['IMSI']
            c[CDR.Called_IMSI] = G.node[e[1]]['IMSI']
            c[CDR.Calling_Latitude] = float(5 * np.random.random_sample() + 35)
            c[CDR.Calling_Longitude] = float(5 * np.random.random_sample() + 70)
            # c[CDR.Called_Latitude] = float(5 * np.random.random_sample() + 35)
            # c[CDR.Called_Longitude] = float(5 * np.random.random_sample() + 70)
            c[CDR.isp_name] = 'random'

            cdr_list.append(c)
            i += 1
    return cdr_list


def generate_duplicate_cdr_data(G):
    data = generate_cdr_data(G)
    num_cdr = len(data)
    print('Generate duplicate cdr data.')
    for i in range(num_cdr):
        cdr = data[i]
        c = init_one_cdr()
        c[CDR.Calling_Number] = cdr[CDR.Called_Number]
        c[CDR.Called_Number] = cdr[CDR.Calling_Number]
        c[CDR.Call_Time] = cdr[CDR.Call_Time]
        c[CDR.Call_Type] = 'voice'
        c[CDR.CDR_Type] = '1'
        c[CDR.Duration_SEC] = cdr[CDR.Duration_SEC]
        c[CDR.Calling_IMEI] = cdr[CDR.Called_IMEI]
        c[CDR.Called_IMEI] = cdr[CDR.Calling_IMEI]
        c[CDR.Calling_IMSI] = cdr[CDR.Called_IMSI]
        c[CDR.Called_IMSI] = cdr[CDR.Calling_IMSI]
        c[CDR.Calling_Latitude] = cdr[CDR.Called_Latitude]
        c[CDR.Calling_Longitude] = cdr[CDR.Called_Longitude]
        # c[CDR.Called_Latitude] = cdr[CDR.Calling_Latitude]
        # c[CDR.Called_Longitude] = cdr[CDR.Calling_Longitude]
        c[CDR.isp_name] = 'random_dup'
        data.append(c)
    return data


if __name__ == '__main__':
    cdr_graph = init_cdr_graph()
    data = generate_duplicate_cdr_data(cdr_graph)
    pass
    # with open('cdr_random_dup.json', 'w') as fp:
    #     print('Save cdr data to json.')
    #     json.dump(data, fp=fp, indent=4)
