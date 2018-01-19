from bc.generators.base import Generator
import networkx as nx
import helper.utilities as ux
import sys

class Class_A_Max_Generator( Generator ) :

	def __init__( self, n, min, max, l, m, k, seed ) :
		Generator.__init__(self)
		self.num_behaviors = n
		self.min_nodes = min
		self.max_nodes = max
		self.num_actions = m
		self.num_acts_per_beh = l
		assert self.num_actions > self.num_acts_per_beh
		self.num_target_seqs = k
		self.problem_name = 'class-A-max-%d-%d-%d-%d-%d-%d-%d'%(seed,n,min,max,l,m,k)
		self.output_folder = 'class-A-max-%d/%d-%d-%d-%d-%d-%d'%(seed,n,min,max,l,m,k)
		self.setup()

	def generate_beh_graphs( self ) :
		self.beh_graphs = []
		self.beh_graphs = ux.generate_random_graphs(self.min_nodes, self.max_nodes, 1,self.num_behaviors)
		ux.allocate_actions(self.beh_graphs,self.num_actions)
		print "Behaviors generated."

	def generate_target_graph( self ) :
		
		dets = []
		## we cannot consider all graphs so let us take first 4
		tgt_graphs = self.beh_graphs[0:3]
		for graph in tgt_graphs:
			graph_det = ux.determinize(graph)
			dets.append(graph_det)
		
		det_systems = ux.cross(dets)
		det_esystems = []
		for system in det_systems:
			det_esystems.append(ux.get_asynchronous_product(system))    
		
		synch_product = det_esystems[0].copy()
		for i in range(len(det_esystems) - 1):
			synch_product = ux.synchronous_product(synch_product, det_esystems[i + 1])
			tnode = synch_product.nodes()[0]
			start = []
			for j in range(len(tnode)):
				start.append(0)
			startnode = tuple(start)
			synch_product = ux.remove_nonreachable_nodes(synch_product, startnode)

		cg_det = ux.get_single_determinized(synch_product)

		tnode = cg_det.nodes()[0]
		startnode = ux.get_startnode(tnode)
		
		cg_det = ux.remove_nonreachable_nodes(cg_det,startnode)
		print "Maximal target generated"
		#collect all nodes that link to the startnode
		end_nodes = []
		paths = []
		for node in cg_det.nodes():
		    if cg_det.has_edge(node, startnode):
		        simple_paths_gen = nx.all_simple_paths(cg_det, startnode, node)
		        simple_paths = list(simple_paths_gen)
		        if(len(simple_paths) > 0):
		            paths.append(simple_paths)
		            end_nodes.append(node)
		
		seq_target = nx.DiGraph()
		seq_target.add_node(0) # 0 is always start node
		
		node_index = 0
		path_index = 0
		for i in range(len(end_nodes)):
		    for path in paths[i]:
		    	  path_index = path_index + 1
		    	  for j in range(len(path) - 1):
		    	  	   node_index = node_index + 1 
		    	  	   seq_target.add_node(node_index)
		    	  	   edge = cg_det.get_edge_data(path[j], path[j + 1])
		    	  	   if(j == 0):
		    	  	   	seq_target.add_edge(0, node_index , label=edge[0]['label'])
		    	  	   else:
		    	  	   	seq_target.add_edge(node_index - 1, node_index, label=edge[0]['label'])
		    	  edge = cg_det.get_edge_data(path[len(path) - 1], startnode)
		    	  seq_target.add_edge(node_index - 1, 0, label=edge[0]['label'])
		    	  if(path_index >= self.num_target_seqs):
		           self.tgt_graph = seq_target
		           return
		self.tgt_graph = seq_target
		
