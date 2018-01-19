import ConfigParser
from itertools import product
import networkx as nx
import random

def read_config(fileName):
    configParser = ConfigParser.ConfigParser()
    configParser.read(fileName)
    return config_section_map(configParser, "Behaviors")

def config_section_map(config, section):
    dict1 = {}
    options = config.options(section)
    for option in options:
        try:
            dict1[option] = config.get(section, option)
            if dict1[option] == -1:
                print("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

def is_orphan(graph, node):
    for othernode in graph.nodes():
        if node != othernode and (graph.has_edge(node, othernode) or graph.has_edge(othernode, node)):
            return False;
    return True

def get_orphans(graph):
    nodes = graph.nodes_with_selfloops()
    orphan = []
    for node in nodes:
        if is_orphan(graph, node):
            orphan.append(node)
    return orphan

def is_reachable(graph, node):
    tree = nx.bfs_tree(graph, node)
    if len(graph.nodes()) == len(tree.nodes()):
        return True;
    return False

def has_cycle(dgraph, node):
    graph = nx.Graph(dgraph)
    cycles = nx.cycle_basis(graph, node);
    for cycle in cycles:
        length = len(cycle)
        if length > 2 and  cycle[length - 1] == node:
            return True
    return False

def get_ndnodes(graph):
    ndnodes = set()
    nodes = graph.nodes()
    for node in nodes:
        edges = graph.edges([node], data=True)
        for edge in edges:
            list = [x for x in edges if edge[2]['label'] == x[2]['label']]
            if len(list) > 1:
                #print list
                ndnodes.add(node)
    return ndnodes


def _dict_product(d1, d2):
    return dict((k, (d1.get(k), d2.get(k))) for k in set(d1) | set(d2))

def get_list(el):
    if type(el) is str:
        return [int(el)]
    if type(el) is int:
        return [el]
    if type(el) is tuple:
        return list(el)
    else:
        print type(el) 

def asynchronous_product(graph1, graph2):
    GH = nx.MultiDiGraph()
    for u, v in product(graph1, graph2):
        n = tuple(get_list(u) + get_list(v))
        #print (n, _dict_product(graph1.node[u], graph2.node[v]))
        GH.add_node(n, _dict_product(graph1.node[u], graph2.node[v]))
            
    for u, v, k, d in graph1.edges_iter(data=True, keys=True):
        for x in graph2:
            #print (u,x),(v,x),k,d
            node1 = tuple(get_list(u) + get_list(x))
            node2 = tuple(get_list(v) + get_list(x))
            #print (node1,node2,d)
            GH.add_edges_from([(node1, node2, d)])   
    
    for x in graph1:
        for u, v, k, d in graph2.edges_iter(data=True, keys=True):
            #print (x,u),(x,v),k,d
            node1 = tuple(get_list(x) + get_list(u))
            node2 = tuple(get_list(x) + get_list(v))
            #print (node1,node2,d)
            GH.add_edges_from([(node1, node2, d)])   
    
    GH.name = "Cartesian product(" + graph1.name + "," + graph2.name + ")"
    return GH

def cross(args):
    ans = [[]]
    for arg in args:
        ans = [x + [y] for x in ans for y in arg]
    return ans

def get_edges_with_label(label, edges):
    result = []
    for edge in edges:
        if edge[len(edge) - 1]['label'] == label:
            result.append(edge)
    return result

def get_labels(edges):
    labels = set([])
    for edge in edges:
        labels.add(edge[len(edge) - 1]['label'])
    return labels

def determinize(graph):
    ndnodes = get_ndnodes(graph)
    graph_edges = []
    for node in ndnodes:
        edges = graph.edges([node], data=True)
        labels = get_labels(edges)
        for label in labels:
            ndedges = get_edges_with_label(label, edges)
            if len(ndedges) > 1:
                graph_edges.append(ndedges)

    det_edges = cross(graph_edges)
    det_behs = []
    for edge_grp in det_edges:
        tmpgraph = graph.copy()
        for g in graph_edges:
            for e in g:
                tmpgraph.remove_edge(e[0], e[1])
        tmpgraph.add_edges_from(edge_grp)
        det_behs.append(tmpgraph)
    return det_behs


def remove_nonreachable_nodes(graph, startnode):    
    tree = nx.bfs_tree(graph, startnode)
    reachable = tree.nodes()
    not_reachable = [item for item in graph.nodes() if item not in reachable]
    graph.remove_nodes_from(not_reachable)
    return graph

def synchronous_product(graph1, graph2):
    GH = nx.MultiDiGraph()
    for u, v in product(graph1, graph2):
        n = tuple(get_list(u) + get_list(v))
        #print (n, _dict_product(graph1.node[u], graph2.node[v]))
        GH.add_node(n, _dict_product(graph1.node[u], graph2.node[v]))
    
    for u1, v1, d1 in graph1.edges_iter(data=True):
        for u2, v2, d2 in graph2.edges_iter(data=True):
            if(d1 == d2):
                node1 = tuple(get_list(u1) + get_list(u2))
                node2 = tuple(get_list(v1) + get_list(v2))
                GH.add_edges_from([(node1, node2, d1)])

    GH.name = "Synchronous product(" + graph1.name + "," + graph2.name + ")"
    return GH

def get_startnode(tnode):
    start = []
    for j in range(len(tnode)):
        start.append(0)
    return tuple(start)

def get_single_determinized(graph):
    ndnodes = get_ndnodes(graph)
    graph_edges = []
    for node in ndnodes:
        edges = graph.edges([node], keys=True, data=True)
        labels = get_labels(edges)
        for label in labels:
            ndedges = get_edges_with_label(label, edges)
            if len(ndedges) > 1:
                graph_edges.append(ndedges)
    
    first_combination = []
    startnode = get_startnode(graph.nodes()[0])
    for edgegrp in graph_edges:
        added = False
        for edge in edgegrp:
            if edge[1] == startnode and not added:
                first_combination.append(edge)
                added = True
        if not added:
            index = random.randrange(0, len(edgegrp), 1)
            first_combination.append(edgegrp[index])
    tmpgraph = graph.copy()
    for g in graph_edges:
        for e in g:
            tmpgraph.remove_edge(e[0], e[1], key=int(e[2]))
    tmpgraph.add_edges_from(first_combination)
    return tmpgraph

def generate_random_graphs(minnodes, maxnodes, maxdegree, num):
    graphs = [] #list to store the graphs
    #actual main loop to generate random graphs
    finished = False
    while not finished:
        nodes = random.randrange(minnodes, maxnodes + 1, 1)
        #generate in and out degrees
        din = []
        dout = []
        for j in range(nodes):
            din.append(random.randrange(1, maxdegree + 1, 1))
            dout.append(random.randrange(1, maxdegree + 1, 1))
        diff = sum(din) - sum(dout)
        if diff < 0:
            dout = din
            diff *= -1
        while diff != 0: #make sure in and out degrees are same
            index = random.randrange(0, nodes, 1) #pick random index
            adjust = random.randrange(1, diff + 1, 1) #pick random adjustment
            if dout[index] + adjust <= maxdegree:
                dout[index] += adjust
                diff -= adjust
    
        G = nx.directed_configuration_model(din, dout) #generate random graph
        if is_reachable(G, G.nodes()[0]) and has_cycle(G, G.nodes()[0]):
            G.graph['name'] = "Graph_" + str(len(graphs))
            graphs.append(G)        
            if len(graphs) >= num:
                finished = True
    return graphs

## remove multiple parallel edges having same action label
def sanitize(graph):
    ndnodes = get_ndnodes(graph)
    toremove = set()
    for node in ndnodes:
        edges = graph.edges([node], data=True)
        for edge in edges:
            elist = [x for x in edges if edge[2]['label'] == x[2]['label']]
            eset = set()
            for el in elist:
                eset.add(el[1])
            if len(elist) != len(eset):
                toremove.add((edge[0], edge[1]))
    graph.remove_edges_from(toremove)
    
def get_cycles(beh,startnode):
    cycles = nx.simple_cycles(beh)
    root_cycles = []
    for cycle in cycles:
        if cycle[0]==startnode:
            root_cycles.append(cycle)
    #print root_cycles
    return root_cycles

## remove multiple parallel edges having same action label
def make_deterministic(graph, actionset):
    ndnodes=get_ndnodes(graph)
    toremove = set()
    for node in ndnodes:
        edges = graph.edges([node],data=True)
        for edge in edges:  
            ndnodes=get_ndnodes(graph) 
            if node in ndnodes:         
                actions = set([x[2]['label'] for x in edges])
                new_actionset = set(actionset).difference(actions)
                if len(new_actionset) == 0:
                    toremove.add((edge[0],edge[1]))
                    graph.remove_edges_from(toremove)
                else:
                    new_action = new_actionset.pop();
                    edge[2]['label']=new_action
                    
                    
def get_cycle(cycles,cycle_len):
    applicable_cycles=[]
    for cycle in cycles:
        if len(cycle)==cycle_len:
            applicable_cycles.append(cycle) 
    if len(applicable_cycles)>0:           
        chosen_cycle = random.randrange(0,len(applicable_cycles),1)
    else:
        chosen_cycle=0
    return applicable_cycles[chosen_cycle]

def has_cycle_of_length(cycles,length):
    for cycle in cycles:
        if len(cycle)==length+1:
            return True
    return False

def get_combination(total,max):
    combination=[]
    count = 0
    while count < total:
        nextstep = random.randrange(1,max+1,1)
        combination.append(nextstep)
        count+=nextstep
    if count>total:
        last_element = combination[len(combination)-1]
        diff = count-total
        if diff==last_element:
            combination.pop(len(combination)-1)
        else:
            combination[len(combination)-1]=last_element-diff
    return combination
 
def allocate_actions(graphs,action_set,all_det=False):
    for graph in graphs:
        add_actions(graph,action_set)
        sanitize(graph)
        if all_det:
            make_deterministic(graph,action_set)    
        #ndnodes = utilities.get_ndnodes(graph)
        #print graph.graph['name'] + " has the following non-deterministic nodes: " + str(ndnodes)

def add_actions(graph,action_set):
    edges = graph.edges(data=True);
    for edge in edges:
        action_index = random.randrange(0,len(action_set))
        edge[2]['label']=action_set[action_index]      
             
        
def get_asynchronous_product(graphs):
    product = graphs[0].copy()
    for i in range(len(graphs) - 1):
        product = asynchronous_product(product, graphs[i + 1])   
    return product     
