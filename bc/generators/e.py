from bc.generators.base import Generator
import networkx as nx
import random
import sys

class Class_E_Generator( Generator ) :

	# p : Proportion of reliable/unreliable
	# r : Redundancy per 'run action'
	# m : Number of 'run actions'
	def __init__( self, r, m ) :
		self.num_run_actions = m
		self.redundancy = r
		self.problem_name = 'class-E-%d-%d'%(r, m)
		self.output_folder = 'class-E-%d-%d'%(r, m )
		self.finish_action = 0
		self.reset_action = 1
		self.prepare_action = range(2, m+2)
		self.run_action = range( m+2, 2*m + 2 )
		self.num_actions = 2*m + 2
		self.setup()

	def create_unreliable_behavior( self, i, j ) :
		b = nx.MultiDiGraph( name = 'beh_unreliable_%d_%d'%(i,j) )
		for i in range(0,4) :
			b.add_node(i)
		b.add_edge( 0, 1, label=self.prepare_action[i] )
		b.add_edge( 1, 2, label=self.run_action[i] )
		b.add_edge( 1, 3, label=self.run_action[i] )
		b.add_edge( 2, 0, label=self.finish_action )
		b.add_edge( 3, 0, label=self.reset_action )
		return b

	def create_reliable_behavior( self, i, j ) :
		b = nx.MultiDiGraph( name = 'beh_unreliable_%d_%d'%(i,j) )
		for i in range(0,3) :
			b.add_node(i)
		b.add_edge( 0, 1, label=self.prepare_action[i] )
		b.add_edge( 1, 2, label=self.run_action[i] )
		b.add_edge( 2, 0, label=self.finish_action )
		return b

	def generate_beh_graphs( self ) :
		self.beh_graphs = []
		for i in range(0, self.num_run_actions ) :
			for j in range( 0, self.redundancy ) :
				self.beh_graphs.append( self.create_unreliable_behavior(i,j) )

	def generate_target_graph( self ) :
		self.tgt_graph = nx.MultiDiGraph( name='target' )
		self.tgt_graph.add_node( 0 )
		state_idx = 1
		for i in range( self.num_run_actions ) :
			p = state_idx
			r = state_idx + 1
			state_idx += 2
			self.tgt_graph.add_node( p )
			self.tgt_graph.add_node( r )
			self.tgt_graph.add_edge( 0, p, label=self.prepare_action[i] )
			self.tgt_graph.add_edge( p, r, label=self.run_action[i] )
			self.tgt_graph.add_edge( r, p, label=self.reset_action )
			self.tgt_graph.add_edge( r, 0, label=self.finish_action )

		
