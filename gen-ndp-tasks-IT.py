#!/usr/bin/python
import sys, os, random
from bc.generators.i import Class_I_Generator
from bc.generators.t import Class_T_Generator
from helper import utilities


def compile_into_ndp(bc_problem):
    bc_problem.make_states()
    bc_problem.make_bc_actions()
    bc_problem.make_transition_relations()

    # bc_problem.print_stats( sys.stdout )

    bc_problem.make_fluents()

    print >> sys.stdout, "# Fluents:", bc_problem.num_fluents()
    # bc_problem.print_fluents()

    bc_problem.make_ndp_actions()
    print >> sys.stdout, "# Actions:", bc_problem.num_ndp_actions()
    bc_problem.make_init()
    bc_problem.make_goal()
    bc_problem.write_PPDDL()
    bc_problem.write_NuGaT_SMV_spec()
    bc_problem.write_SMV_spec()
    bc_problem.write_ISPL_spec()


def main():
    seed = int(sys.argv[1])
    random.seed(seed)

    num_behs = [10, 20, 40]
    num_actions = [5, 10, 20]
    k_divs = [2, 4]

    for b in num_behs:
        for m in num_actions:
            for k_div in k_divs:
                prob_gen = Class_I_Generator(b, 2, 5, 4, m, m / k_div, 5, seed)
                prob_gen.generate_behaviors()
                prob_gen.generate_target()
                compile_into_ndp(prob_gen.problem)

                prob_gen = Class_T_Generator(b, 2, 5, 4, m, m / k_div, 5, seed)
                prob_gen.generate_behaviors()
                prob_gen.generate_target()
                compile_into_ndp(prob_gen.problem)


if __name__ == '__main__':
    main()
