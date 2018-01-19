import networkx as nx
import os
from bc.problem import Problem

class Generator :
	
	def __init__( self ) :
		self.problem_name = None
		self.output_folder = None

	def setup( self ) :
		assert self.problem_name is not None
		assert self.output_folder is not None
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
			#os.system( 'dot -Tpdf -o%s %s'%(beh_out_pdf_file, beh_out_file) ) 
			self.problem.beh_graphs.append( self.beh_graphs[i].copy() )

	def generate_target( self ) :
		self.generate_target_graph( )
		nx.draw_graphviz(self.tgt_graph)
		target_out_file = os.path.join( self.output_folder, "target.dot" )
		target_out_pdf_file = os.path.join( self.output_folder, "target.pdf" )
		nx.write_dot(self.tgt_graph, target_out_file)
		#os.system( 'dot -Tpdf -o%s %s'%(target_out_pdf_file, target_out_file) )
		self.problem.tgt_graph = self.tgt_graph.copy()

	def generate_beh_graphs( self ) :
		raise RuntimeError, "Method not implemented!"

	def generate_target_graph( self ) :
		raise RuntimeError, "Method not implemented!"
