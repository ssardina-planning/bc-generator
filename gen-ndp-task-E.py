#!/usr/bin/python
import sys, os, random
from bc.generators.e import Class_E_Generator
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

	num_actions_set = [ 5, 10, 15, 20, 25 ]
	redundancy_regime = [ 1, 2, 3, 4 ]	

	for redundancy in redundancy_regime : 
		for num_actions in num_actions_set :
			prob_gen = Class_E_Generator( redundancy, num_actions )
			prob_gen.generate_behaviors()
			prob_gen.generate_target()
			compile_into_ndp( prob_gen.problem )

if __name__ == '__main__' :
	main()
