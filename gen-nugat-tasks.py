#!/usr/bin/python
import sys, os, random
from bc.generators.a import Class_A_Generator
from bc.generators.b import Class_B_Generator
from bc.generators.c import Class_C_Generator
from bc.generators.d import Class_D_Generator
from bc.generators.a_max import Class_A_Max_Generator
from helper import utilities
import gc

def compile_into_ndp( bc_problem, det_beh = True ) :
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
	bc_problem.write_SMV_spec( )
	bc_problem.write_NuGaT_SMV_spec( )
	if det_beh :
		bc_problem.write_ISPL_spec( )
	

def generate_class_A( n, l, m, k, seed ) :

	prob_gen = Class_A_Generator( n, l, m, k, seed )
	prob_gen.generate_behaviors()
	prob_gen.generate_target()
	
	compile_into_ndp( prob_gen.problem )
	del prob_gen.problem
	del prob_gen

def generate_class_A_Max(n, min, max, l, m, k, seed ) :
	
	prob_gen = Class_A_Max_Generator( n, min, max, l, m, k, seed )
	prob_gen.generate_behaviors()
	prob_gen.generate_target()
	
	compile_into_ndp(prob_gen.problem)
	del prob_gen.problem
	del prob_gen
	
	
def generate_class_B( n, l, p, m, k, seed ) :

	prob_gen = Class_B_Generator( n, l, p, m, k, seed )
	prob_gen.generate_behaviors()
	prob_gen.generate_target()
	
	compile_into_ndp( prob_gen.problem, True )
	del prob_gen.problem
	del prob_gen

def generate_class_C( n, l, m, b, d, seed ) :

	prob_gen = Class_C_Generator( n, l, m, b, d, seed )

	prob_gen.generate_behaviors()
	prob_gen.generate_target()
	
	compile_into_ndp( prob_gen.problem, True )
	del prob_gen.problem
	del prob_gen

def generate_class_D( n, l, p, m, b, d, seed ) :

	prob_gen = Class_D_Generator( n, l, p, m, b, d, seed )
	
	prob_gen.generate_behaviors()
	prob_gen.generate_target()

	compile_into_ndp( prob_gen.problem, True )
	del prob_gen.problem
	del prob_gen



def main() :
	
	random.seed( 4711 )
	generate_class_A( 10, 1, 5, 2, 4711 )
	generate_class_A( 10, 1, 5, 10, 4711 )


if __name__ == '__main__' :
	main()
