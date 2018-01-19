import os
import networkx as nx
from problem import Problem
import random
import sys

class Problem_Generator :

	def __init__( self, n, l, m, k, seed ) :
		self.num_behaviors = n
		self.num_actions = m
		self.num_acts_per_beh = l
		assert self.num_actions > self.num_acts_per_beh
		self.num_target_seqs = k
		self.problem_name = 'class-A-%d-%d-%d-%d-%d'%(seed,n,l,m,k)
		self.output_folder = 'class-A-%d/%d-%d-%d-%d'%(seed,n,l,m,k)
		if not os.path.exists( self.output_folder ) :
			os.makedirs( self.output_folder )
		self.problem = Problem()
		self.problem.num_actions = self.num_actions
		self.problem.name = self.problem_name
		self.problem.output_folder = self.output_folder

	def generate_behaviors( self ) :
		
		self.generate_beh_graphs( )
		for i in range( len( self.beh_graphs ) ) :
			nx.draw_graphviz( self.beh_graphs[i] )
			beh_out_file = os.path.join( self.output_folder, 'beh-%d.dot'%i )
			beh_out_pdf_file = os.path.join( self.output_folder, 'beh-%d.pdf'%i )
			nx.write_dot( self.beh_graphs[i], beh_out_file )
			os.system( 'dot -Tpdf -o%s %s'%(beh_out_pdf_file, beh_out_file) ) 
			self.problem.beh_graphs.append( self.beh_graphs[i].copy() )

	def generate_target( self ) :
		self.generate_target_graph( )
		nx.draw_graphviz(self.tgt_graph)
		target_out_file = os.path.join( self.output_folder, "target.dot" )
		target_out_pdf_file = os.path.join( self.output_folder, "target.pdf" )
		nx.write_dot(self.tgt_graph, target_out_file)
		os.system( 'dot -Tpdf -o%s %s'%(target_out_pdf_file, target_out_file) )
		self.problem.tgt_graph = self.tgt_graph.copy()
	
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
			self.beh_graphs.append( b ) 

	def generate_target_request_sequences( self ) :
		seqs = []
		prefixes = range(self.num_actions)
		while len(prefixes) > 0 and len(seqs) < self.num_target_seqs :
			a0 = random.choice(prefixes)
			prefixes.remove(a0)
			num_a0 =  self.num_target_seqs / self.num_actions
			if num_a0 == 0 : num_a0 = 1
			print >> sys.stdout, "Generating", num_a0 , "with prefix", a0
			for j in range( num_a0 ) :
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
				
				
