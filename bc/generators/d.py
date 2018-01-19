from bc.generators.base import Generator
import networkx as nx
import random
import sys

class Class_D_Generator( Generator ) :

	def __init__( self, n, l, p, m, b, d, seed ) :
		Generator.__init__(self)
		self.num_behaviors = n
		self.num_actions = m
		self.num_acts_per_beh = l
		self.prob_failure = p
		assert self.num_actions > self.num_acts_per_beh
		self.tgt_branching_factor = b
		self.tgt_depth = d
		self.problem_name = 'class-D-%d-%d-%d-%d-%d-%d-%d'%(seed,n,l,p*100,m,b,d)
		self.output_folder = 'class-D-%d/%d-%d-%d-%d-%d-%d'%(seed,n,l,p*100,m,b,d)
		self.setup()

	def generate_beh_graphs( self ) :
		self.beh_graphs = []
		for i in range( self.num_behaviors ) :
			b = nx.MultiDiGraph( name = 'beh_%d'%i )
			for j in range( self.num_acts_per_beh ) :
				b.add_node( j )
			for j in range( self.num_acts_per_beh - 1 ) :
				b.add_edge( j, j+1 )
			b.add_edge( self.num_acts_per_beh - 1, 0 )
			behavior_actions = random.sample( range(0, self.num_actions), self.num_acts_per_beh )
			random.shuffle( behavior_actions )
			for e, action in zip( b.edges(data=True), behavior_actions ) :
				e[2]['label'] = action
			state_idx = len(b.nodes())
			for n in b.nodes() :
				for e in b.edges( [ n ], data = True ) :
					if random.random() <= self.prob_failure :
						act = e[2]['label']
						b.add_node( state_idx )
						b.add_edge( n, state_idx, label=act )
						state_idx += 1
			self.beh_graphs.append( b ) 


	def generate_target_graph( self ) :
		self.tgt_graph = nx.MultiDiGraph( name='target' )
		self.tgt_graph.add_node( 0 )
		requests = random.sample( xrange(0,self.num_actions), self.tgt_branching_factor )
		succs = []
		s = 0
		for a in requests :
			sp = self.generate_tree( s, self.tgt_depth )	
			succs.append( sp )
			s = sp
		for i in range(0, len(requests)) :
			self.tgt_graph.add_edge( 0, succs[i], label=requests[i] )

		

	def generate_tree( self, parent, d ) :
		requests = random.sample( xrange(0,self.num_actions), self.tgt_branching_factor )
		if d == 0 :
			s = parent + 1
			self.tgt_graph.add_node( s )
			for a in requests :
				self.tgt_graph.add_edge( s, 0, label=a )
			return s
		
		succs = []
		s = parent
		for a in requests :
			sp = self.generate_tree( s, d - 1 )
			succs.append( sp )
			s = sp
		s = max(succs) + 1
		for i in range(0, len(requests)) :
			self.tgt_graph.add_edge( s, succs[i], label=requests[i] )
		return s
