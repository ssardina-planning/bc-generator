#!/usr/bin/python
import sys, os, random
from bc.generators.a_u import Class_A_U_Generator
from helper import utilities

def compile_into_ndp( bc_problem ) :
	bc_problem.make_states()
	bc_problem.make_bc_actions()
	bc_problem.make_transition_relations()

	#bc_problem.print_stats( sys.stdout )

	bc_problem.make_fluents()

	print >> sys.stdout, "# Fluents:", bc_problem.num_fluents()
	#bc_problem.print_fluents()

	bc_problem.make_ndp_actions()
	print >> sys.stdout, "# Actions:", bc_problem.num_ndp_actions()
	bc_problem.make_init()
	bc_problem.make_goal()
	bc_problem.write_PPDDL( )
	bc_problem.write_NuGaT_SMV_spec()
	bc_problem.write_SMV_spec()
	bc_problem.write_ISPL_spec()

def main() :

	seed = int(sys.argv[1])
	random.seed( seed )
	
	num_unreliable = [ 2, 4, 8, 16 ]
	num_actions = [ 5, 10, 15, 20 ]
	target_lens = [ 2, 4, 8, 16 ]

	for n in num_unreliable :
		for m in num_actions :
			for k in target_lens :
				prob_gen = Class_A_U_Generator( n, m, k, seed )
				prob_gen.generate_behaviors()
				prob_gen.generate_target()
				compile_into_ndp( prob_gen.problem )
	
if __name__ == '__main__' :
	main()
