import sys
import os

class Behavior :

	def __init__( self, index ) :
		self.index = index
		self.B = {}
		self.b0 = None
		self.trans = []

	def add_state(self, q ) :
		self.B[q] = 'b_%d_%d'%(self.index,q)

	def print_stats( self, stream ) :
		print >> stream, "Behavior #%d"%self.index
		print >> stream, "|B| =", len(self.B), "b_0 =", self.b0, "|Delta| =", len(self.trans)
		print >> stream, "Transitions:"
		for t in self.trans :
			print >> stream, t

	def make_fluents( self ) :
		self.fluents = []
		self.fluent = {}
		for q in self.B.values() :
			signature = '(state_%s)'%q 
			self.fluents.append( signature )
			self.fluent[ q ] = signature

	def applicable( self, a ) :
		app = []	
		for qi, ap, qj in self.trans :
			if a == ap :
				app.append( qi )
		return app

	def resulting( self, q, a ) :
		res = []
		for qi, ap, qj in self.trans :
			if qi == q and ap == a :
				res.append( qj )
		return res		
class Target :
	
	def __init__( self ) :
		self.T = {}
		self.t0 = []
		self.trans = []

	def add_state( self, t ) :
		try :
			self.T[t] = 't' + '_'.join([ str(i) for i in t])
		except TypeError :
			self.T[t] = 't_%s'%t

	def print_stats( self, stream ) :
		print >> stream, "Target"
		print >> stream, "|T| =", len(self.T), "t_0 =", self.t0, "|Delta| =", len(self.trans)
		print >> stream, "Transitions:"
		for t in self.trans :
			print >> stream, t

	def make_fluents( self ) :
		self.fluents = []
		self.fluent = {}
		for q in self.T.values() :
			signature = '(state_%s)'%q 
			self.fluents.append( signature )
			self.fluent[ q ] = signature

	def requests( self, q ) :
		reqs = []
		for qi, a, qj in self.trans :
			if qi == q :
				reqs.append( a )
		return reqs

	def reachable( self, q, a ) :
		reach = []
		for qi, ap, qj in self.trans :
			if qi == q and ap == a :
				reach.append( qj )
		return reach

class	NDP_Action :

	def __init__(self) :
		self.name = None
		self.precondition = []
		self.effects = []

	def declaration( self ) :
		return """
		(:action %s
			:precondition %s
			:effect %s
		)
		"""%(self.name, self.precondition, self.effects)

def PPDDL_conjunction( formulas ) :
	formula_str = ' '.join( formulas )
	return '(and %s )'%formula_str

def PPDDL_negation( p ) :
	return '(not %s)'%p

def PPDDL_one_of( formulas ) :
	formula_seq = ' '.join( formulas )
	return '(oneof %s )'%formula_seq

def PPDDL_cond_eff( cond, eff ) :

	formula_str = ' '.join( [cond, eff] )
	return '(when %s)'%formula_str

class Problem :

	def __init__( self ) :
		self.tgt_graph = None
		self.beh_graphs = []
		self.target = None
		self.behaviors = []
		self.actions = {}
		self.num_actions = None

	def print_stats( self, stream ) :
		for beh in self.behaviors :
			beh.print_stats(stream)
		self.target.print_stats(stream)

	def make_states( self ) :
		index = 0
		for beh in self.beh_graphs :
			b = Behavior( index )
			for n in beh.nodes_iter() :
				b.add_state(n)
			index += 1
			b.b0 = b.B[0]
			self.behaviors.append(b)
		self.target = Target()
		for t in self.tgt_graph.nodes_iter() :
			self.target.add_state( t )
		self.target.t0 = self.target.T[self.tgt_graph.nodes()[0]]
				 

	def make_bc_actions( self ) :
		for i in range(0,self.num_actions) :
			self.actions[i] = 'a_%d'%i

	def make_transition_relations( self ) :
		for i in range(0, len(self.behaviors) ):
			beh = self.behaviors[i]
			graph = self.beh_graphs[i]
			for qi, qj, data in graph.edges_iter( data=True ) :
				beh.trans.append( ( beh.B[qi], self.actions[data['label']], beh.B[qj] ) ) 

		for qi, qj, data in self.tgt_graph.edges_iter(data=True) :
			self.target.trans.append( ( self.target.T[qi], self.actions[data['label']], self.target.T[qj] ) )

	def make_fluents( self ) :
		self.global_fluents = []
		self.needs_start = '(needs_start)'
		self.global_fluents.append( self.needs_start )
		self.started = '(started)'
		self.global_fluents.append( self.started )

		for beh in self.behaviors :
			beh.make_fluents()

		self.target.make_fluents()

		self.action_fluents = []
		self.served = {}
		self.requested = {}
		self.satisfied = []

		# Make action fluents
		for _, a in self.actions.items() :
			served_sig = '(served_%s)'%a
			requested_sig = '(requested_%s)'%a
			self.action_fluents.append( served_sig )
			self.served[a] = served_sig
			self.action_fluents.append( requested_sig )
			self.requested[a] = requested_sig

		# Make meta-level fluents
		self.meta_fluents = []
		self.loop_finished = '(loop_finished)'
		self.meta_fluents.append( self.loop_finished )
		self.loop_started = '(loop_started)'
		self.meta_fluents.append( self.loop_started )

		self.required = {}
		self.end = {}
		for beh in self.behaviors :
			self.make_meta_fluents( beh.fluents )
		self.make_meta_fluents( self.target.fluents )
		self.make_meta_fluents( self.global_fluents ) 
	
		self.valid = '(valid)'
		self.meta_fluents.append( self.valid )
	
		# Union
		self.fluents = self.global_fluents + self.action_fluents
		for beh in self.behaviors :
			self.fluents += beh.fluents
		self.fluents += self.target.fluents

	def make_meta_fluents( self, fluents ) :
		for p in fluents :
			req_signature = '(required_%s)'%p.replace('(','').replace(')','')
			end_signature = '(end_%s)'%p.replace('(','').replace(')','')
			self.required[p] = req_signature
			self.end[p] = end_signature
			self.meta_fluents.append( req_signature )
			self.meta_fluents.append( end_signature )
	
	def num_fluents( self ) :
		return len(self.fluents) + len(self.meta_fluents)
	
	def print_fluents( self, stream = sys.stdout ) :
		for p in self.fluents :
			print p	
		for p in self.meta_fluents :
			print p

	def make_ndp_actions( self ) :
		self.ndp_actions = []
		self.make_init_target()
		self.make_progress_target()
		self.make_delegate_actions()
		self.make_meta_actions()

	def num_ndp_actions( self ) :
		return len(self.ndp_actions)


	def normalize( self, action ) :
		action.precondition = PPDDL_conjunction( action.precondition )
		action.effects = PPDDL_conjunction( action.effects ) 
		return action

	def make_init_target( self ) :
		
		for _, t in self.target.T.items() :
			action = NDP_Action()
			action.name = 'generate_request_%s'%t
			action.precondition.append( self.target.fluent[t] )
			action.precondition.append( self.needs_start )

			action.effects.append( PPDDL_negation( self.needs_start ) )
			#action.effects.append( self.started )
	
			one_of_effs = [ self.requested[a] for a in self.target.requests( t ) ]	
			if len(one_of_effs) == 1 :
				action.effects.append( one_of_effs[0] )
			else :	
				action.effects.append( PPDDL_one_of( one_of_effs ) )

			action = self.normalize( action )
			#print >> sys.stdout, action.declaration()
			self.ndp_actions.append( action )

	def make_progress_target( self ) :
		for _, t in self.target.T.items() :
			for _, a in self.actions.items() :
				next_tgt = self.target.reachable( t, a )
				if len(next_tgt) == 0 : continue
				assert len(next_tgt) == 1
				action = NDP_Action()
				action.name = 'progress_target_%s_%s'%(t,a)

				action.precondition.append( self.target.fluent[t] )
				#action.precondition.append( self.started )
				action.precondition.append( self.served[a] )

				#if len(next_tgt) == 1 :
				action.effects.append( self.target.fluent[next_tgt[0]] )
				action.effects.append( self.valid )	
				#else :
				#	one_of_effs = [ self.target.fluent[tp] for tp in next_tgt ]
				#	action.effects.append( PPDDL_one_of( one_of_effs ) )
				action.effects.append( self.needs_start )
				#if next_tgt[0] == self.target.t0 :
				#	action.effects.append( PPDDL_cond_eff( self.loop_started, self.loop_finished ) )
				action.effects.append( PPDDL_negation( self.target.fluent[t] ) )	
				#action.effects.append( PPDDL_negation( self.started ) )
				action.effects.append( PPDDL_negation( self.served[a] ) )
				
				action = self.normalize( action )
				# print >> sys.stdout, action.# declaration()
				self.ndp_actions.append( action )

				

	def make_delegate_actions( self ) :

		for beh in self.behaviors :
			beh_del_effs = {}		
			for qi, a, qj in beh.trans :
				try :
					beh_del_effs[ (qi, a) ].append( qj )
				except KeyError :
					beh_del_effs[ (qi, a) ] = [qj]
				
			for pre, eff_list in beh_del_effs.iteritems() :
				qi, a = pre
				action = NDP_Action()
				action.name = 'delegate_%s_to_%s'%(a,qi)
				action.precondition.append( beh.fluent[qi] )
				action.precondition.append( self.requested[a] )
				#action.precondition.append( self.started )
				
				if len( eff_list ) == 1 :
					action.effects.append( beh.fluent[ eff_list[0] ] )
				else :
					one_of_effs = [ beh.fluent[qj] for qj in eff_list ]
					action.effects.append( PPDDL_one_of( one_of_effs ) )
				action.effects.append( self.served[a] )
				action.effects.append( PPDDL_negation( beh.fluent[qi] ) )
				action.effects.append( PPDDL_negation( self.requested[a] ) )
				#action.effects.append( PPDDL_negation( self.started ) )

				action = self.normalize( action )
				#print >> sys.stdout, action.declaration()
				self.ndp_actions.append( action )
					
				

#		for _, a in self.actions.items() :
#			for beh in self.behaviors :
#				valid_states = beh.applicable( a )
#				if len( valid_states ) == 0 : continue
#				for b in valid_states :
#					action = NDP_Action()
#					action.name = 'delegate_%s_to_%s'%(a,b)
					
#					action.precondition.append( beh.fluent[b] )
#					action.precondition.append( self.requested[a] )
#					action.precondition.append( self.started )
#					action.precondition.append( self.valid )	

#					res_b_states = beh.resulting( b, a )
#					if len( res_b_states) == 1 :
#						action.effects.append( beh.fluent[res_b_states[0]] )
#					else :
#						one_of_effs = [ beh.fluent[bp] for bp in res_b_states ]
#						action.effects.append( PPDDL_one_of( one_of_effs ) )
#					action.effects.append( self.served[a] )
#					action.effects.append( PPDDL_negation( beh.fluent[b] ) )
#					action.effects.append( PPDDL_negation( self.requested[a] ) )
					#action.effects.append( PPDDL_negation( self.started ) )

#					action = self.normalize( action )
					# print >> sys.stdout, action.declaration()
#					self.ndp_actions.append( action )

	def make_loop_actions( self ) :
		#for t in [self.target.t0] :#self.target.T.items() :
		#for _, t in #self.target.T.items() :
		action = NDP_Action()

		#action.name = 'loop_%s'%t
		action.name = 'loop'

		#action.precondition.append( self.target.fluent[t] )
		action.precondition.append( self.needs_start )
		action.precondition.append( PPDDL_negation( self.loop_started ) )
		#action.precondition.append( self.valid )	
	
		action.effects.append( self.loop_started )
		action.effects.append( PPDDL_negation( self.valid ) )
		for p in self.fluents :
			condition = p
			try :
				eff = [ self.required[p], PPDDL_negation( self.end[p] ) ]
			except KeyError :
				continue
			action.effects.append( PPDDL_cond_eff( condition, PPDDL_conjunction(eff) ) )

		action = self.normalize(action )
		# print >> sys.stdout, action.declaration()
		self.ndp_actions.append( action )

	def make_end_action( self ) :
		action = NDP_Action()

		action.name = 'end'
		
		action.precondition.append( self.loop_started )
		action.precondition.append( self.valid )	
	
		action.effects.append( PPDDL_negation( self.loop_started ) )
		action.effects.append( self.loop_finished )
		for p in self.fluents :
			try :
				cond = PPDDL_conjunction( [ p, self.required[p] ] )
			except KeyError :
				continue
			eff = self.end[p]
			action.effects.append( PPDDL_cond_eff( cond, eff ) )

		action = self.normalize(action)
		# print >> sys.stdout, action.declaration()
		self.ndp_actions.append(action)
	
	def make_meta_actions( self ) :
		self.make_loop_actions()
		self.make_end_action()

	def num_actions( self ) :
		return len(self.ndp_actions)

	def make_init( self ) :
		self.init = []
		self.init.append( self.target.fluent[self.target.t0] )
		self.init.append( self.needs_start )
		
		for beh in self.behaviors :
			self.init.append( beh.fluent[beh.b0] )
		
		for p in self.fluents :
			try :
				self.init.append( self.end[p] )
			except KeyError :
				continue
		#self.init.append( self.valid )

	def make_goal( self ) :
		self.goal = []
		self.goal.append( self.loop_finished )
		for sat_fl in self.satisfied :
			self.goal.append( sat_fl )
		#self.goal.append( self.target.fluent[self.target.t0] )
		for p in self.fluents :
			try :
				self.goal.append( self.end[p] )
			except KeyError :
				continue

	def write_PPDDL( self ) :
		domain_file_name = os.path.join( self.output_folder, 'domain.ppddl' )
		instance_file_name = os.path.join( self.output_folder, 'instance.ppddl' )		

		self.write_domain_file( domain_file_name )
		self.write_instance_file( instance_file_name )
		
		#MRJ: Make tarball
		current_dir = os.getcwd()
		os.chdir( self.output_folder )
		os.system( 'tar jcvf problem-%s.tar.bz2 domain.ppddl instance.ppddl'%( self.name ) )
		os.chdir( current_dir )

	def write_domain_file( self, fname ) :
		with open( fname, 'w' ) as outstream :
			print >> outstream, "(define (domain %s)"%self.name
			print >> outstream, "\t(:requirements :non-deterministic :negative-preconditions :strips)"
			self.write_predicates( outstream )
			self.write_actions( outstream )
			print >> outstream, ")"

	def write_predicates( self, stream ) :
		print >> stream, "\t(:predicates"
		for p in self.fluents :
			print >> stream, "\t\t", p
		for p in self.meta_fluents :
			print >> stream, "\t\t", p
		print >> stream, "\t)"	

	def write_actions( self, stream ) :
		for a in self.ndp_actions :		
			print >> stream, a.declaration()

	def write_instance_file( self, fname ) :
		with open( fname, 'w' ) as out :
			print >> out, "(define (problem %s-init-goal)"%self.name
			print >> out, "\t(:domain %s)"%self.name
			print >> out, "\t(:init"
			for p in self.init :
				print >> out, "\t\t", p
			print >> out, "\t)"
			print >> out, "\t(:goal"
			print >> out, "\t\t(and"
			for p in self.goal :
				print >> out, "\t\t\t", p
			print >> out, "\t\t)"
			print >> out, "\t)"
			print >> out, ")"

	def write_NuGaT_SMV_spec( self ) :
		nugat_spec_filename = os.path.join( self.output_folder, '%s.nugat.smv'%self.name )

		with open( nugat_spec_filename, 'w' ) as outstream :
			self.write_nugat_behavior_modules( outstream )
			self.write_nugat_target_module( outstream )
			print >> outstream, "GAME"
			print >> outstream, ""
			self.write_nugat_opp_player( outstream )
			self.write_nugat_control_player( outstream )
			self.write_nugat_goal_formula( outstream )

	def write_nugat_behavior_modules( self, stream ) :
		for i in xrange(0,len( self.behaviors )) :
			b_i = self.behaviors[i]
			print >> stream, "MODULE Beh%d(a,j)"%i
			# Define state variables
			print >> stream, "VAR"
			state_list = []
			for _, b_state in b_i.B.iteritems() :
				state_list.append( b_state )
			print >> stream, "\tstate: { fail, %s };"%','.join( state_list )
			print >> stream, "INIT"
			print >> stream, "\tstate = %s"%b_i.b0
			# Define transitions
			print >> stream, "TRANS"
			print >> stream, "\tcase"
			# if no action is delegated to the behavior, the state is unchanged
			print >> stream, "\t\t!(j = %d) : next(state) = state;"%i
			for qi, a, qj in b_i.trans :
				print >> stream, "\t\tstate = %s & a = %s : next(state) = %s;"%(qi, a, qj)
			# if none of the above applies, go to failed state
			print >> stream, "\t\tTRUE : next(state) = fail;"
			print >> stream, "\tesac"
			print >> stream, ""

	def write_nugat_target_module( self, stream ) :
		print >> stream, "MODULE Target(req)"
		print >> stream, "VAR"
		state_list = []
		for _, t_state in self.target.T.iteritems() :
			state_list.append( t_state )
		print >> stream, "\tstate : { impossible, %s };"%','.join(state_list)
		print >> stream, "INIT"
		print >> stream, "\tstate = %s"%self.target.t0
		print >> stream, "TRANS"
		print >> stream, "\tcase"
		for ti, a, tj in self.target.trans :
			print >> stream, "\t\tstate = %s & req = %s : next(state) = %s;"%(ti, a, tj)
		print >> stream, "\t\tTRUE : next(state) = impossible;"
		print >> stream, "\tesac"
		print >> stream, ""
		
	def write_nugat_opp_player( self, stream ) :
		print >> stream, "PLAYER_1"
		print >> stream, "VAR"
		for i in range(0, len(self.behaviors) ) :
			print >> stream, "\tb%d : Beh%d(req,index);"%(i,i)
		print >> stream, "\tt: Target(req);"
		print >> stream, "\treq : { %s };"%','.join( [ a for _, a in self.actions.iteritems() ] )

		for _, t in self.target.T.iteritems() :
			reqs = self.target.requests( t )
			print >> stream, "TRANS"	
			if len(reqs) == 1 :
				print >> stream, "\tt.state = %s -> req = %s"%(t,reqs[0])
			else :
				print >> stream, "\tt.state= %s -> req in { %s }"%(t, ','.join(reqs) )
		print >> stream, ""

	def write_nugat_control_player( self, stream ) :
		print >> stream, "PLAYER_2"
		print >> stream, "VAR"
		print >> stream, "\tindex: {%s};"%','.join( [ str(i) for i in xrange(0,len(self.behaviors)) ] )
		print >> stream, ""

	def write_nugat_goal_formula( self, stream ) :
		terms = [ 'b%d.state = fail'%i for i in xrange(0,len(self.behaviors)) ]
		print >> stream, "AVOIDTARGET PLAYER_2 ( %s )"%' | '.join(terms)
	
	def write_SMV_spec( self ) :
		smv_spec_filename = os.path.join( self.output_folder, '%s.smv'%self.name )
		
		with open( smv_spec_filename, 'w' ) as outstream :
			self.write_behavior_modules( outstream )
			self.write_target_module( outstream )
			self.write_available_behavior_system( outstream )
			self.write_client_module( outstream )
			self.write_environment_module( outstream )
			self.write_controller_module( outstream )
			self.write_main_module( outstream )

	def write_behavior_module( self, i, stream ) :
		b_i = self.behaviors[i]
		print >> stream, "MODULE Beh%d(a,j)"%i
		# Define state variables
		print >> stream, "VAR"
		state_list = []
		for _, b_state in b_i.B.iteritems() :
			state_list.append( b_state )
		print >> stream, "\tstate: { start, failed, %s };"%','.join( state_list )
		print >> stream, "INIT"
		print >> stream, "\tstate = start"
		# Define transitions
		print >> stream, "TRANS"
		print >> stream, "\tcase"
		# 'start' transition
		print >> stream, "\t\tstate = start & a = start_op : next(state) = %s;"%b_i.b0
		# if no action is delegated to the behavior, the state is unchanged
		print >> stream, "\t\ta = none | !(j = %d) : next(state) = state;"%i
		for qi, a, qj in b_i.trans :
			print >> stream, "\t\tstate = %s & a = %s : next(state) = %s;"%(qi, a, qj)
		# if none of the above applies, go to failed state
		print >> stream, "\t\tTRUE : next(state) = failed;"
		print >> stream, "\tesac"

		# Bind initial and fail states
		print >> stream, "DEFINE"
		print >> stream, "\tinitial := state = start;"
		print >> stream, "\tfail := state = failed;"
		print >> stream, ""
		print >> stream, ""

	def write_behavior_modules( self, stream ) :
		for i in range( 0, len(self.behaviors) ) :
			self.write_behavior_module( i, stream )
			

	def write_target_module( self, stream ) :
		print >> stream, "MODULE Target(req)"
		print >> stream, "VAR"
		state_list = []
		for _, t_state in self.target.T.iteritems() :
			state_list.append( t_state )
		print >> stream, "\tstate : { start, %s };"%','.join(state_list)
		print >> stream, "INIT"
		print >> stream, "\tstate = start & req = start_op"
		print >> stream, "TRANS"
		print >> stream, "\tcase"
		print >> stream, "\t\tstate = start & req = start_op : next(state) = %s;"%self.target.t0
		print >> stream, "\t\treq = none : next(state) = state;"
		for ti, a, tj in self.target.trans :
			print >> stream, "\t\tstate = %s & req = %s : next(state) = %s;"%(ti, a, tj)
		print >> stream, "\t\tTRUE : FALSE;"
		print >> stream, "\tesac"
		print >> stream, "DEFINE"
		print >> stream, "\tinitial := state = start;"
		print >> stream, ""
		print >> stream, ""

	def write_available_behavior_system( self, stream ) :
		print >> stream, "MODULE AvailableSystem( req, index )"
		print >> stream, "VAR"
		for i in range(0, len(self.behaviors) ) :
			print >> stream, "\tb%d : Beh%d(req,index);"%(i,i)
		print >> stream, "DEFINE"
		print >> stream, "\tinitial := %s;"%'&'.join( [ "b%d.initial"%i for i in range(0, len(self.behaviors)) ] )
		print >> stream, "\tfail := %s;"%'&'.join( [ "b%d.fail"%i for i in range(0, len(self.behaviors)) ] )
		print >> stream, ""
		print >> stream, ""

	def write_client_module( self, stream ) :
		print >> stream, "MODULE Client"
		print >> stream, "VAR"
		print >> stream, "\ttarget : Target(req);"
		print >> stream, "\treq : { start_op, none, %s };"%','.join( [ a for _, a in self.actions.iteritems() ] )
		print >> stream, "INIT"
		print >> stream, "req = start_op"
		print >> stream, "TRANS"
		print >> stream, "\tcase"
		for _, t in self.target.T.iteritems() :
			reqs = self.target.requests( t )
			if len(reqs) == 1 :
				print >> stream, "\t\tnext(tstate) = %s : next(req) = %s;"%(t,reqs[0])
			else :
				print >> stream, "\t\tnext(tstate) = %s : next(req) in { %s };"%(t, ','.join(reqs) )
		print >> stream, "\t\tFALSE : next( req ) = none;"
		print >> stream, "\tesac"
		print >> stream, "DEFINE"
		print >> stream, "\tinitial := target.initial;"
		print >> stream, "\ttstate := target.state;"
		print >> stream, ""
		print >> stream, ""


	def write_environment_module( self, stream ) :
		print >> stream, "MODULE System( index )"
		print >> stream, "VAR"
		print >> stream, "\tavailsys : AvailableSystem( client.req, index );"
		print >> stream, "\tclient : Client;"
		print >> stream, "DEFINE"
		print >> stream, "\tinitial := availsys.initial & client.initial;"
		print >> stream, "\tfail := availsys.fail;"
		print >> stream, "\tfailure := fail;"
		print >> stream, ""
		print >> stream, ""


	def write_controller_module( self, stream ) :
		print >> stream, "MODULE Controller"
		print >> stream, "VAR"
		print >> stream, "\tindex : { %s };"%','.join([ str(i) for i in range(0,len(self.behaviors))])
		print >> stream, "INIT"
		print >> stream, "\tindex = 1"
		print >> stream, "TRANS"
		print >> stream, "\tTRUE"
		print >> stream, ""
		print >> stream, ""


	def write_main_module( self, stream ) :
		print >> stream, "MODULE main"
		print >> stream, "VAR"
		print >> stream, "\tsys : system System(contr.index);"
		print >> stream, "\tcontr : system Controller;"
		print >> stream, "DEFINE"
		print >> stream, "\tgood := sys.initial | !(sys.failure);"
		print >> stream, ""
		print >> stream, ""

	def write_ISPL_spec( self ) :
		smv_spec_filename = os.path.join( self.output_folder, '%s.ispl'%self.name )
		
		with open( smv_spec_filename, 'w' ) as outstream :
			self.write_header(outstream)
			self.write_controller_agent(outstream)
			self.write_behavior_agents(outstream)
			self.write_target_agent(outstream)
			self.write_evaluation_rule(outstream)
			self.write_initial_states(outstream)
			self.write_groups(outstream)
			self.write_safety_goal(outstream)

	def write_header( self, stream ) :
		print >> stream, "Semantics = SA;"
		print >> stream, ""

	def write_controller_agent( self, stream ) :
		beh_name_list = [ 'Beh%d'%i for i in range(0,len(self.behaviors)) ]
		action_name_list = [ name for _, name in self.actions.iteritems() ]
		cs_beh_names = ', '.join( beh_name_list )
		cs_action_names = ', '.join( action_name_list )
		print >> stream, "Agent Environment"
		print >> stream, "\tObsvars:"
		print >> stream, "\t\tselected_beh : { start, %s };"%cs_beh_names
		print >> stream, "\t\tact : { start, %s };"%cs_action_names
		print >> stream, "\tend Obsvars"
		print >> stream, "\tActions = { start, %s };"%cs_beh_names
		print >> stream, "\tProtocol:"
		print >> stream, "\t\tact = start : {start};"
		print >> stream, "\t\tOther: { %s};"%cs_beh_names
		print >> stream, "\tend Protocol"
		print >> stream, "\tEvolution:"
		for beh in beh_name_list :
			print >> stream, "\t\tselected_beh = %(beh)s if Action = %(beh)s;"%locals()
		for action in action_name_list :
			print >> stream, "\t\tact = %(action)s if T.Action = %(action)s;"%locals()
		print >> stream, "\tend Evolution"
		print >> stream, "end Agent"
		print >> stream, ""
	
	def write_behavior_agents( self, stream ) :
		for i in range( 0, len(self.behaviors) ) :
			beh_name = 'Beh%d'%i
			beh = self.behaviors[i]
			beh_states = [ b for _, b in beh.B.iteritems() ]
			cs_beh_states_names = ', '.join( beh_states )
			print >> stream, "Agent %s"%beh_name
			print >> stream, "\tVars:"
			print >> stream, "\t\tstate : { err, %s};"%cs_beh_states_names
			print >> stream, "\tend Vars"
			print >> stream, "\tActions = { err, %s };"%cs_beh_states_names
			print >> stream, "\tProtocol:"
			for bi, a, bj in beh.trans :
				print >> stream, "\t\tstate = %s and Environment.act = %s : {%s};"%(bi, a, bj )
			print >> stream, "\t\tOther : {err};"	
			print >> stream, "\tend Protocol"
			print >> stream, "\tEvolution:"
			print >> stream, "\t\tstate = err if Action=err and Environment.Action = %s;"%beh_name
			for _, b in beh.B.iteritems() :
				print >> stream, "\t\tstate = %s if Action = %s and Environment.Action = %s;"%(b,b,beh_name)
			print >> stream, "\tend Evolution"
			print >> stream, "end Agent"
			print >> stream, ""

	def write_target_agent( self, stream ) :
		action_name_list = [ name for _, name in self.actions.iteritems() ]
		cs_action_names = ', '.join( action_name_list )
		target_states = [ t for _, t in self.target.T.iteritems() ]
		cs_target_names = ', '.join(target_states)
		print >> stream, "Agent T"
		print >> stream, "\tVars:"
		print >> stream, "\t\tstate : { %s };"%cs_target_names
		print >> stream, "\tend Vars"
		print >> stream, "\tActions = { %s };"%cs_action_names
		print >> stream, "\tProtocol:"
		print >> stream, "\t\tEnvironment.act = start : { %s };"%', '.join( self.target.requests( self.target.t0) )
		for ti, a, tj in self.target.trans :
			next_state_actions = ', '.join( self.target.requests( tj ) )
			print >> stream, "\t\tstate = %s and Environment.act = %s : { %s };"%(ti, a, next_state_actions)
		print >> stream, "\tend Protocol"
		print >> stream, "\tEvolution:"
		for ti, a, tj in self.target.trans :
			print >> stream, "\t\tstate = %s if state = %s and Environment.act = %s;"%(tj,ti,a)
		print >> stream, "\tend Evolution"
		print >> stream, "end Agent"
		print >> stream, ""

	def write_evaluation_rule( self, stream ) :
		print >> stream, "Evaluation"
		formula = []
		for i in range( 0, len(self.behaviors) ) :
			formula.append( 'Beh%d.state = err'%i )
		print >> stream, "\tError if %s;"%' or '.join(formula)
		print >> stream, "end Evaluation"
		print >> stream, ""

	def write_initial_states( self, stream ) :
		print >> stream, "InitStates"
		formula = []
		for i in range(0, len(self.behaviors)) :
			formula.append( 'Beh%d.state = %s'%(i, self.behaviors[i].b0 ) )
		formula.append( 'T.state = %s'%self.target.t0 )
		formula.append( 'Environment.act = start' )
		formula.append( 'Environment.selected_beh = start' )
		print >> stream, "%s;"%' and '.join( formula )
		print >> stream, "end InitStates"
		print >> stream, ""

	def write_groups( self, stream ) :
		print >> stream, "Groups"
		print >> stream, "\tController = {Environment};"
		print >> stream, "end Groups"
		print >> stream, ""

	def write_safety_goal( self, stream ) :
		print >> stream, "Formulae"
		print >> stream, "\t<Controller> G (!Error);"
		print >> stream, "end Formulae"

