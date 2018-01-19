#!/usr/bin/python
import networkx as nx
from helper import utilities
from itertools import product


graph1 = nx.read_dot("./s_beh0.dot")
graph2 = nx.read_dot("./s_beh1.dot")
graph3 = nx.read_dot("./beh2.dot") 

graphs=[]
graphs.append(graph1)
graphs.append(graph2)


## do the asynchronous product of the behaviors
product = graphs[0].copy()
for i in range(len(graphs)-1):
    product=utilities.asynchronous_product(product,graphs[i+1])

print "Enacted system generated"

nx.draw_graphviz(product)
nx.write_dot(product,"enacted_system.dot")

print "Enacted system written to dot"

dets = []
total=[]
for graph in graphs:
    graph_det = utilities.determinize(graph)
    total.append(len(graph_det))
    dets.append(graph_det)

print "Behaviors determinised (" + str(total) + ")"

det_systems = utilities.cross(dets)
det_esystems = []
for system in det_systems:
    det_prod = system[0].copy()
    for i in range(len(system)-1):
        det_prod = utilities.asynchronous_product(det_prod,system[i+1])
    det_esystems.append(det_prod)
    
print "Determinised enacted systems created (" + str(len(det_esystems)) + ")"

for i in range(len(det_esystems)):
    nx.draw_graphviz(det_esystems[i])
    nx.write_dot(det_esystems[i],"d_s_"+str(i)+".dot")

synch_product = det_esystems[0].copy()
for i in range(len(det_esystems)-1):
    synch_product=utilities.synchronous_product(synch_product,det_esystems[i+1])
    tnode = synch_product.nodes()[0]
    start = []
    for j in range(len(tnode)):
        start.append(0)
    startnode = tuple(start)
    synch_product = utilities.remove_nonreachable_nodes(synch_product, startnode)
    print "done " + str(i) + " current size: " + str(len(synch_product.nodes()))

print "Synchronous product generated"

nx.draw_graphviz(synch_product)
nx.write_dot(synch_product,"synchronous_product.dot")

print "Synchronous product written to dot"

cg_det = utilities.get_single_determinized(synch_product)

tnode = cg_det.nodes()[0]
startnode = utilities.get_startnode(tnode)

cg_det = utilities.remove_nonreachable_nodes(cg_det,startnode)
print "Target processed"

target_cycles = nx.simple_cycles(cg_det)
for cycle in target_cycles:
    print cycle

nx.draw_graphviz(cg_det)
nx.write_dot(cg_det,"target.dot")

'''
tnode = prod.nodes()[0]
start = []
for i in range(len(tnode)):
    start.append(0)
startnode = tuple(start)

prod = ux.remove_nonreachable_nodes(prod, startnode)

nx.draw_graphviz(prod)
nx.write_dot(prod,"synch.dot")
'''
