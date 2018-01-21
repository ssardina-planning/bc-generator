#!/usr/bin/python
import networkx as nx
from helper import utilities
import os
from networkx.drawing.nx_agraph import read_dot, write_dot, graphviz_layout


# Generate a .pdf file  picture from a .dot file using the dot external software
def generate_dot_image(file_dot):
    path, filename = os.path.split(file_dot)
    filename_pdf = filename.split(".")[0]
    file_pdf = os.path.join(path, filename_pdf)
    os.system('dot -Tpdf -o%s %s' % (file_pdf + ".pdf", file_dot))

file_beh1 = "./test/beh1nd.dot"
file_beh2 = "./test/beh2.dot"
file_beh3 = "./test/beh3.dot" # not used

## Load three behaviors
beh1 = read_dot(file_beh1)
beh2 = read_dot(file_beh2)
# beh3 = read_dot(file_beh3)    # not used

generate_dot_image(file_beh1)
generate_dot_image(file_beh2)
generate_dot_image(file_beh3)


available_system = []
available_system.append(beh1)
available_system.append(beh2)

#################################
# Build the asynchronous product between behavor 1 and 2 (enacted system)
#################################
product = available_system[0].copy()
for i in range(len(available_system) - 1):
    product = utilities.asynchronous_product(product, available_system[i + 1])

nx.draw(product, pos=graphviz_layout(product))
write_dot(product, "test/asynchronous_product.dot")
generate_dot_image("test/asynchronous_product.dot")

print("1. Asynchronous system (enacted system) with behaviors 1 and 2 generated and written to do")


#################################
# Build the asynchronous product between (some) deterministic behavior 1 and 2 (enacted system)
#################################

## First determinise the behaviors in some way...
det_behaviors = []
total = []
for graph in available_system:
    graph_det = utilities.determinize(graph)
    total.append(len(graph_det))
    det_behaviors.append(graph_det)

print("2. Behaviors 1 and 2 determinised (" + str(total) + ")")

det_systems = utilities.cross(det_behaviors)
det_esystems = []
for system in det_systems:
    det_prod = system[0].copy()
    for i in range(len(system) - 1):
        det_prod = utilities.asynchronous_product(det_prod, system[i + 1])
    det_esystems.append(det_prod)

for i in range(len(det_esystems)):
    nx.draw(det_esystems[i], pos=graphviz_layout(det_esystems[i]))
    write_dot(det_esystems[i], "test/d_s_" + str(i) + ".dot")
    generate_dot_image("test/d_s_" + str(i) + ".dot")

print("3. Asynchronous system between determinised behaviors 1 and 2 created (" + str(len(det_esystems)) + ")")


synch_product = det_esystems[0].copy()
for i in range(len(det_esystems) - 1):
    synch_product = utilities.synchronous_product(synch_product, det_esystems[i + 1])
    tnode = list(synch_product.nodes)[0]
    start = []
    for j in range(len(tnode)):
        start.append(0)
    startnode = tuple(start)
    synch_product = utilities.remove_nonreachable_nodes(synch_product, startnode)
    print "done " + str(i) + " current size: " + str(len(synch_product.nodes()))

nx.draw(synch_product, pos=graphviz_layout(synch_product))
write_dot(synch_product, "test/synchronous_product.dot")
generate_dot_image("test/synchronous_product.dot")

print("4. Synchronous product generated and written to dot")

cg_det = utilities.get_single_determinized(synch_product)
tnode = list(cg_det.nodes)[0]
startnode = utilities.get_startnode(tnode)

cg_det = utilities.remove_nonreachable_nodes(cg_det, startnode)
print "5. Target processed"

target_cycles = nx.simple_cycles(cg_det)
for cycle in target_cycles:
    print cycle

nx.draw(cg_det, pos=graphviz_layout(cg_det))
write_dot(cg_det, "test/target.dot")
generate_dot_image("test/target.dot")

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
