from bc.generators.base import Generator
import networkx as nx
import helper.utilities as ux
import sys, copy, random
import bc.problem as problem

class Class_T_Generator( Generator ) :

	def __init__( self, n, min, max,l,  m, k, d,seed ) :
		Generator.__init__(self)
		self.num_behaviors = n
		self.min_nodes = min
		self.max_nodes = max
		self.max_degree = l
		self.num_actions = m
		self.target_branch = k
		self.target_depth = d+1
		assert self.max_nodes * self.num_behaviors > self.target_depth
		self.problem_name = 'class-T-%d-%d-%d-%d-%d-%d-%d-%d'%(seed,n,min,max,l,m,k,d)
		self.output_folder = 'class-T-%d/%d-%d-%d-%d-%d-%d-%d'%(seed,n,min,max,l,m,k,d)
		self.setup()

	def generate_beh_graphs( self ) :
		self.beh_graphs = []
		self.beh_graphs = ux.generate_random_graphs(self.min_nodes, self.max_nodes, self.max_degree,self.num_behaviors)
		actionset = [x for x in range(self.num_actions)]
		ux.allocate_actions(self.beh_graphs,actionset,True)
		print "Behaviors generated."
	
	def beh_cycles_exist(self,combination,beh_cycle_index):
		for j in combination:
			applicable_behaviors = beh_cycle_index[j]
			if len(applicable_behaviors)==0:
				return False
		return True
	
	def add_sequence(self,tgt_spec,start_actions,beh_cycles,beh_cycle_index):
		start_node = len(tgt_spec.nodes())
		prev_node = 0
		next_node = start_node
		chosen=False
		while not chosen:
			combination = ux.get_combination(self.target_depth,self.max_nodes)
			start_cycle = combination[0]
			poss_behaviors = beh_cycle_index[start_cycle]
			if len(poss_behaviors)>0:
				if len(poss_behaviors)>1:
					applicable_index = random.randrange(0,len(poss_behaviors),1)
				else:
					applicable_index = 0
				behavior = poss_behaviors[applicable_index]
				chosen_cycle = ux.get_cycle(beh_cycles[behavior], start_cycle + 1)
				edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[0],chosen_cycle[1])
				chosen_edge = random.randrange(0,len(edge_data),1)
				edge = list(edge_data.values())[chosen_edge]
				if edge['label'] not in start_actions:
					tgt_spec.add_node(next_node)
					tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
					prev_node=next_node
					next_node+=1
					start_actions.append(edge['label'])
					# check if cycles exist for rest of combination
					if (self.beh_cycles_exist(combination,beh_cycle_index)):
						chosen=True
		
		## finish the first cycle
		for k in range(1,start_cycle):
			edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[k],chosen_cycle[k+1])
			chosen_edge = random.randrange(0,len(edge_data),1)
			edge = list(edge_data.values())[chosen_edge]
			tgt_spec.add_node(next_node)				
			tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
			prev_node=next_node
			next_node+=1
			
		## finish the rest of sequence
		for l in range(1,len(combination)):
			j = combination[l]
			#print j
			applicable_behaviors = beh_cycle_index[j]
			#print applicable_behaviors
			if len(applicable_behaviors) > 0:
				applicable_index = random.randrange(0, len(applicable_behaviors), 1)
			else:
				applicable_index = 0
			behavior = applicable_behaviors[applicable_index]
			chosen_cycle = ux.get_cycle(beh_cycles[behavior], j + 1)
			for k in range(0,j):
				edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[k],chosen_cycle[k+1])
				chosen_edge = random.randrange(0,len(edge_data),1)
				edge = list(edge_data.values())[chosen_edge]
				if next_node-start_node==self.target_depth-1:
					tgt_spec.add_edges_from([(prev_node,0,{'label':edge['label']})])
				else:
					tgt_spec.add_node(next_node)				
					tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
					prev_node=next_node
					next_node+=1
					
		## add branch after first beh seq
		count=0
		branch_point=combination[0]
		branch_node = start_node+branch_point - 1
		prev_node = branch_node
		next_node = len(tgt_spec.nodes())
		if tgt_spec.has_edge(prev_node,prev_node+1):
			exclude_action_edge=tgt_spec.get_edge_data(prev_node,prev_node+1)
		else:
			exclude_action_edge=tgt_spec.get_edge_data(prev_node,0)
		exculde_action = exclude_action_edge[0]['label']
		chosen=False
		while not chosen:
			combination =  ux.get_combination(self.target_depth-branch_point,self.max_nodes)
			start_cycle = combination[0]
			poss_behaviors = beh_cycle_index[start_cycle]
			if len(poss_behaviors)>0:
				if len(poss_behaviors)>1:
					applicable_index = random.randrange(0,len(poss_behaviors),1)
				else:
					applicable_index = 0
				behavior = poss_behaviors[applicable_index]
				chosen_cycle = ux.get_cycle(beh_cycles[behavior], start_cycle + 1)
				edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[0],chosen_cycle[1])
				chosen_edge = random.randrange(0,len(edge_data),1)
				edge = list(edge_data.values())[chosen_edge]
				if edge['label'] !=exculde_action:
					if count==self.target_depth-branch_point-1:
						tgt_spec.add_edges_from([(prev_node,0,{'label':edge['label']})])
					else:
						tgt_spec.add_node(next_node)
						tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
						prev_node=next_node
						next_node+=1
						count+=1
					# check if cycles exist for rest of combination
					if (self.beh_cycles_exist(combination,beh_cycle_index)):
						chosen=True
		
		## finish the first cycle
		for k in range(1,start_cycle):
			edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[k],chosen_cycle[k+1])
			chosen_edge = random.randrange(0,len(edge_data),1)
			edge = list(edge_data.values())[chosen_edge]
			if count==self.target_depth-branch_point-1:
				tgt_spec.add_edges_from([(prev_node,0,{'label':edge['label']})])
			else:
				tgt_spec.add_node(next_node)				
				tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
				prev_node=next_node
				next_node+=1
				count+=1
			
		## finish the rest of sequence
		for l in range(1,len(combination)):
			j = combination[l]
			#print j
			applicable_behaviors = beh_cycle_index[j]
			#print applicable_behaviors
			if len(applicable_behaviors) > 0:
				applicable_index = random.randrange(0, len(applicable_behaviors), 1)
			else:
				applicable_index = 0
			behavior = applicable_behaviors[applicable_index]
			chosen_cycle = ux.get_cycle(beh_cycles[behavior], j + 1)
			for k in range(0,j):
				edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[k],chosen_cycle[k+1])
				chosen_edge = random.randrange(0,len(edge_data),1)
				edge = list(edge_data.values())[chosen_edge]
				if count==self.target_depth-branch_point-1:
					tgt_spec.add_edges_from([(prev_node,0,{'label':edge['label']})])
				else:
					tgt_spec.add_node(next_node)				
					tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
					prev_node=next_node
					next_node+=1
					count+=1
		'''	
		count=0
		for j in combination:
			applicable_behaviors = beh_cycle_index[j]
			if len(applicable_behaviors) > 0:
				applicable_index = random.randrange(0, len(applicable_behaviors), 1)
			else:
				applicable_index = 0
			behavior = applicable_behaviors[applicable_index]
			chosen_cycle = ux.get_cycle(beh_cycles[behavior], j + 1)
			for k in range(0,j):
				edge_data = self.beh_graphs[behavior].get_edge_data(chosen_cycle[k],chosen_cycle[k+1])
				chosen_edge = random.randrange(0,len(edge_data),1)
				edge = list(edge_data.values())[chosen_edge]
				if count==self.target_depth-branch_point-1:
					tgt_spec.add_edges_from([(prev_node,0,{'label':edge['label']})])
				else:
					tgt_spec.add_node(next_node)				
					tgt_spec.add_edges_from([(prev_node,next_node,{'label':edge['label']})])
					prev_node=next_node
					next_node+=1
					count+=1
		'''
		return tgt_spec

	def generate_target_graph( self ) :
		beh_cycles=[]
		for beh in self.beh_graphs:
			beh_cycles.append(ux.get_cycles(beh,0))
		beh_cycle_index=[]
		beh_cycle_index.append([]) #no cycles with length 0
		for i in range(1,self.max_nodes+1):
			cycles=[]
			for j in range(len(self.beh_graphs)):
				if ux.has_cycle_of_length(beh_cycles[j],i):
					cycles.append(j)
			beh_cycle_index.append(cycles)

		tgt_spec = nx.MultiDiGraph()
		tgt_spec.add_node(0) #start node
		start_actions=[]
		for i in range(self.target_branch):
			tgt_spec=self.add_sequence(tgt_spec,start_actions,beh_cycles,beh_cycle_index)
						
		self.tgt_graph = tgt_spec
