from bc.generators.base import Generator
import networkx as nx
import random
import sys

class Class_A_U_Generator( Generator ) :

	def __init__( self, n,  m, k, seed ) :
		Generator.__init__(self)
		self.num_behaviors = n
		self.num_actions = m
		#self.num_acts_per_beh = l
		#self.beh_unreliable_ratio=n
		assert self.num_actions > 0
		self.num_target_seqs = k
		self.problem_name = 'class-A-U-%d-%d-%d-%d'%(seed,n,m,k)
		self.output_folder = 'class-A-U-%d/%d-%d-%d'%(seed,n,m,k)
		self.setup()

	def generate_beh_graphs( self ) :
		self.beh_graphs = []
		for i in range( self.num_actions ) :
			b = nx.MultiDiGraph( name = 'beh_%d'%i )
			b.add_node(0)
			b.add_edges_from([(0,0,{'label':i})])
			self.beh_graphs.append( b ) 
			
			#generate n more unreliable behaviors
			for i in range(self.num_behaviors):
				beh = b.copy()
				last_node = len(beh.nodes())-1
				last_edge_data = beh.get_edge_data(last_node,0)
				last_action = last_edge_data[0]['label']
				next_node=len(beh.nodes())
				beh.add_node(next_node)
				beh.add_edges_from([(last_node,next_node,{'label':last_action})])
				self.beh_graphs.append(beh)

	def generate_target_request_sequences( self ) :
		seqs = []
		prefixes = range(self.num_actions)
		heads = []
		while len(prefixes) > 0 and len(seqs) < self.num_target_seqs :
			a0 = random.choice(prefixes)
			prefixes.remove(a0)
			done = False
			while not done :
				actions = range(0,self.num_actions)
				actions.remove(a0)
				random.shuffle( actions )
				seq = [a0] + actions
				if seq not in seqs :
					done = True
					seqs.append(seq)
		return seqs
					

	def generate_target_graph( self ) :
		self.tgt_graph = nx.MultiDiGraph( name='target' )
		target_requests = self.generate_target_request_sequences()
		print >> sys.stdout, len(target_requests), "generated"
		if len(target_requests) == 0 :
			print >> sys.stdout, "Check parameters: no target requests were generated!" 
		self.tgt_graph.add_node( 0 )
		next_state = 1
		for seq in target_requests :
			self.tgt_graph.add_node( next_state )
			self.tgt_graph.add_edge( 0, next_state, label=seq[0] )
			for i in range(1,len(seq)-1) :
				next_state += 1
				self.tgt_graph.add_node( next_state )
				self.tgt_graph.add_edge( next_state - 1, next_state, label = seq[i] )
			self.tgt_graph.add_edge( next_state, 0, label = seq[len(seq)-1] )
			next_state +=1
	
		
