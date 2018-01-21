import os
import networkx as nx
import os
import random
from helper import utilities
from problem import Problem
from networkx.drawing.nx_agraph import graphviz_layout
from networkx.drawing.nx_agraph import write_dot


####################### FUNCTIONS ################################################

def generate_chain_graphs( num_beh, min_states, max_states, num_actions ) :

    assert num_actions >= max_states
    graphs = []

    for i in range( 0, num_beh ) :
        num_states = random.randint( min_states, max_states )
        # Create nodes
        b = nx.MultiDiGraph( name = 'beh_%d'%i )
        for j in range( 0, num_states ) :
            b.add_node( j )
        for j in range( 0, num_states-1 ) :
            b.add_edge( j, j+1 )
        b.add_edge( num_states - 1, 0 )
        for e, a in zip( b.edges( data=True ), random.sample( range(0, num_actions), len( b.edges() ) ) ) :
            e[2]['label'] = a
        graphs.append(b)
    return graphs

def generate_deterministic_target( max_degree, num_actions ) :

    t = nx.MultiDiGraph( name='target' )
    for i in range(0,num_actions) :
        t.add_node( i )

    actions = range(0,num_actions)
    random.shuffle( actions )

    for i in range(0,num_actions-1) :
        t.add_edge( i, i+1 )
    t.add_edge( num_actions-1, 0 )
    for e, a in zip( t.edges( data=True ), actions ) :
        e[2]['label']=a

    return t



def generate_random_graphs(minnodes,maxnodes,maxdegree):
    graphs=[] #list to store the graphs
    #actual main loop to generate random graphs
    finished = False
    while not finished:
        nodes = random.randrange(minnodes,maxnodes+1,1)
        #generate in and out degrees
        din=[]
        dout=[]
        for j in range(nodes):
            din.append(random.randrange(1,maxdegree+1,1))
            dout.append(random.randrange(1,maxdegree+1,1))
        diff = sum(din)-sum(dout)
        if diff<0:
            dout = din
            diff*=-1
        while diff != 0: #make sure in and out degrees are same
            index = random.randrange(0,nodes,1) #pick random index
            adjust = random.randrange(1,diff+1,1) #pick random adjustment
            if dout[index]+adjust <=maxdegree:
                dout[index]+=adjust
                diff -=adjust

        G=nx.directed_configuration_model(din,dout) #generate random graph
        if utilities.is_reachable(G, G.nodes()[0]) and utilities.has_cycle(G,G.nodes()[0]):
            G.graph['name'] = "Graph_"+str(len(graphs))
            graphs.append(G)
            if len(graphs)>=behaviors:
                finished = True
    return graphs

## remove multiple parallel edges having same action label
def sanitize(graph):
    ndnodes=utilities.get_ndnodes(graph)
    toremove = set()
    for node in ndnodes:
        edges = graph.edges([node],data=True)
        for edge in edges:
            elist = [x for x in edges if edge[2]['label'] == x[2]['label']]
            eset = set()
            for el in elist:
                eset.add(el[1])
            if len(elist) != len(eset):
                toremove.add((edge[0],edge[1]))
    graph.remove_edges_from(toremove)

def allocate_actions(actions, graphs):
    for graph in graphs:
        add_actions(actions, graph)
        sanitize(graph)
        ndnodes = utilities.get_ndnodes(graph)
        print graph.graph['name'] + " has the following non-deterministic nodes: " + str(ndnodes)

def add_actions(actions, graph):
    edges = graph.edges(data=True);
    for edge in edges:
        action = random.randrange(0,actions)
        edge[2]['label']=action

def get_asynchronous_product(graphs):
    product = graphs[0].copy()
    for i in range(len(graphs)-1):
        product=utilities.asynchronous_product(product,graphs[i+1])
    return product
################################################################################

class Problem_Generator :

    def __init__( self, config ) :
        print config
        #sample values to test with
        self.num_behaviors =int(config['number'])
        size = config['size'].split('-')
        self.minnodes=int(size[0])
        self.maxnodes=int(size[1])
        self.actions=int(config['actions'])
        self.maxdegree=int(config['maxdegree'])
        self.outputfolder = config['outputfolder']
        if not os.path.exists(self.outputfolder):
            os.makedirs(self.outputfolder)
        self.problem = Problem()

    def generate_behaviors( self ) :
        ##Step 1: Generate random graphs which can be used as behaviors
        #self.graphs = generate_random_graphs( self.num_behaviors, self.minnodes, self.maxnodes, self.maxdegree)
        print "Graphs generated"

        ##Step 2: Allocate actions to edges, clean the graph
        #allocate_actions(self.actions, self.graphs)

        self.graphs = generate_chain_graphs( self.num_behaviors, self.minnodes, self.maxnodes, self.actions )
        print "Behaviors generated"

        ##Step 3: Save the behaviors to file
        for i in range(len(self.graphs)):
            nx.draw_networkx(self.graphs[i], pos=graphviz_layout(self.graphs[i]))
            # nx.draw_graphviz(self.graphs[i])
            beh_out_file = os.path.join( self.outputfolder, 'beh%d.dot'%i )
            beh_out_pdf_file = os.path.join( self.outputfolder, 'beh%d.pdf'%i )
            write_dot(self.graphs[i], beh_out_file )
            self.problem.beh_graphs.append( self.graphs[i].copy() )
            print "Behavior #%d written to file"%i, beh_out_file
            os.system( 'dot -Tpdf -o%s %s'%(beh_out_pdf_file, beh_out_file ) )
        self.problem.num_actions = self.actions

    def compute_enacted_system( self ) :
        ##Step 4: do the asynchronous product of the behaviors and save in file (Not needed as such, just generated to cross check)
        self.asynch_product = get_asynchronous_product( self.graphs )
        print "Enacted system generated"
        nx.draw_graphviz(self.asynch_product)

        enacted_sys_out_file = os.path.join( self.outputfolder, "enacted_system.dot" )
        nx.write_dot( self.asynch_product, enacted_sys_out_file )
        print "Enacted system written to file", enacted_sys_out_file

    def determinize_behaviors( self ) :
        ##Step 5: Get all the determinisations of the behaviors
        self.dets = []
        self.total=[]
        for graph in self.graphs:
            graph_det = utilities.determinize( graph )
            self.total.append(len(graph_det))
            self.dets.append(graph_det)
        print "Behaviors determinised (" + str(self.total) + ")"

    def compute_async_product_of_determinized_behs( self ) :
        ##Step 6: Generate asynchronous product of behavior determinisations
        self.det_systems = utilities.cross(self.dets)
        self.det_esystems = []
        for system in self.det_systems:
            #det_prod = system[0].copy()
            #for i in range(len(system)-1):
            #det_prod = utilities.asynchronous_product(det_prod,system[i+1])
            self.det_esystems.append(get_asynchronous_product(system))
        print "Determinised enacted systems created (" + str(len(self.det_esystems)) + ")"

    def compute_maximum_guarantee( self ) :
        ##Step 7: Do the synchronous product of the enacted systems to get the maximum guarantee
        self.synch_product = self.det_esystems[0].copy()
        for i in range(len(self.det_esystems)-1):
            self.synch_product=utilities.synchronous_product(self.synch_product,self.det_esystems[i+1])
            tnode = self.synch_product.nodes()[0]
            start = []
            for j in range(len(tnode)):
                start.append(0)
            startnode = tuple(start)
            self.synch_product = utilities.remove_nonreachable_nodes(self.synch_product, startnode)

            print "done " + str(i) + " current size: " + str(len(self.synch_product.nodes()))

        print "Synchronous product generated"

        nx.draw_networkx(self.synch_product, graphviz_layout(self.synch_product))
        sync_prod_out_file = os.path.join( self.outputfolder, "synchronous_product.dot" )
        write_dot(self.synch_product, sync_prod_out_file )

        print "Synchronous product written to file", sync_prod_out_file

    def compute_simple_target( self ) :
        self.problem.tgt_graph = generate_deterministic_target( self.maxdegree, self.actions )
        nx.draw_graphviz(self.problem.tgt_graph)
        target_out_file = os.path.join( self.outputfolder, "target.dot" )
        target_out_pdf_file = os.path.join( self.outputfolder, "target.pdf" )
        nx.write_dot(self.problem.tgt_graph, target_out_file)
        os.system( 'dot -Tpdf -o%s %s'%(target_out_pdf_file, target_out_file) )


    def compute_target( self ) :
        self.determinize_behaviors()
        self.compute_async_product_of_determinized_behs()
        self.compute_maximum_guarantee()

        ##Step 8: Extract a maximal deterministic target
        ###OBSERVATION: Maximum guarantee is a non-deterministic behavior.
        ###!! ND-TARGETS are more expressive than Determinitic Targets
        self.cg_det = utilities.get_single_determinized(self.synch_product)

        tnode = list(self.cg_det.nodes)[0]
        startnode = utilities.get_startnode(tnode)

        self.cg_det = utilities.remove_nonreachable_nodes(self.cg_det,startnode)
        print "Target generated"

        nx.draw_networkx(self.cg_det, graphviz_layout(self.cg_det))
        target_out_file = os.path.join( self.outputfolder, "target.dot" )
        target_out_pdf_file = os.path.join( self.outputfolder, "target.pdf" )
        write_dot(self.cg_det, target_out_file)

        print "Target written to file:", target_out_file
        os.system( 'dot -Tpdf -o%s %s'%(target_out_pdf_file, target_out_file) )
        self.problem.tgt_graph = self.cg_det.copy()
