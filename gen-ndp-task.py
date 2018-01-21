#!/usr/bin/python
import sys, os, random
from bc.generators.a import Class_A_Generator
from bc.generators.b import Class_B_Generator
from bc.generators.c import Class_C_Generator
from bc.generators.d import Class_D_Generator
from bc.generators.a_max import Class_A_Max_Generator
from helper import utilities
import gc


def compile_into_ndp(bc_problem, det_beh=True):
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
    bc_problem.write_SMV_spec()
    bc_problem.write_NuGaT_SMV_spec()
    if det_beh:
        bc_problem.write_ISPL_spec()


def generate_class_A(n, l, m, k, seed):
    prob_gen = Class_A_Generator(n, l, m, k, seed)
    prob_gen.generate_behaviors()
    prob_gen.generate_target()

    compile_into_ndp(prob_gen.problem)
    del prob_gen.problem
    del prob_gen


def generate_class_A_Max(n, min, max, l, m, k, seed):
    prob_gen = Class_A_Max_Generator(n, min, max, l, m, k, seed)
    prob_gen.generate_behaviors()
    prob_gen.generate_target()

    compile_into_ndp(prob_gen.problem)
    del prob_gen.problem
    del prob_gen


def generate_class_B(n, l, p, m, k, seed):
    prob_gen = Class_B_Generator(n, l, p, m, k, seed)
    prob_gen.generate_behaviors()
    prob_gen.generate_target()

    compile_into_ndp(prob_gen.problem, True)
    del prob_gen.problem
    del prob_gen


def generate_class_C(n, l, m, b, d, seed):
    prob_gen = Class_C_Generator(n, l, m, b, d, seed)

    prob_gen.generate_behaviors()
    prob_gen.generate_target()

    compile_into_ndp(prob_gen.problem, True)
    del prob_gen.problem
    del prob_gen


def generate_class_D(n, l, p, m, b, d, seed):
    prob_gen = Class_D_Generator(n, l, p, m, b, d, seed)

    prob_gen.generate_behaviors()
    prob_gen.generate_target()

    compile_into_ndp(prob_gen.problem, True)
    del prob_gen.problem
    del prob_gen


def main():
    if len(sys.argv) != 2:
        sys.exit("Please provide random seed")
    # sys.exit("Please provide the config file containing benchmark parameters.")

    seeds = []
    try:
        seeds.append(int(sys.argv[1]))
    except ValueError:
        print >> sys.stderr, "Input argument wasn't a seed (integer)!"
        sys.exit(1)

    action_intervals = [5, 10, 15]
    failure_probs = [0.25, 0.5]
    # (b,min_d,max_d)
    target_params = [(1, 2, 4), (2, 2, 3), (3, 2, 3)]
    # (redundancy, min_actions_beh, max_actions_beh )
    beh_proportions = [1, 2, 3, 4]
    # Number of processes (classes A and B)
    num_plans = [2, 4, 8, 16]

    for seed in seeds:

        random.seed(seed)
        print >> sys.stdout, "Setting seed to", seed
        # class C
        for m in action_intervals:
            for k, d_min, d_max in target_params:
                for n in beh_proportions:
                    b = m * n
                    for d in range(d_min, d_max + 1):
                        print >> sys.stdout, "Generating problem with parameters:"
                        print >> sys.stdout, "m=%(m)d, k=%(k)d, d=%(d)d, b=%(b)d" % locals()
                        generate_class_C(b, 1, m, k, d, seed)
        print >> sys.stdout, "Collecting garbage"
        n = gc.collect()
        print >> sys.stdout, n, "Unreachable objects"
        # class D
        for m in action_intervals:
            for k, d_min, d_max in target_params:
                for n in beh_proportions:
                    for p in failure_probs:
                        b = int(m * (1.0 + p)) * n
                        for d in range(d_min, d_max + 1):
                            print >> sys.stdout, "Generating problem with parameters:"
                            print >> sys.stdout, "m=%(m)d, p=%(p)f, k=%(k)d, d=%(d)d, b=%(b)d" % locals()
                            # generate_class_D( b, 1, p, m, k, d, seed )
        print >> sys.stdout, "Collecting garbage"
        n = gc.collect()
        print >> sys.stdout, n, "Unreachable objects"

        # class A
        for m in action_intervals:
            for k in num_plans:
                for n in beh_proportions:
                    b = m * n
                    print >> sys.stdout, "Generating problem with parameters:"
                    print >> sys.stdout, "m=%(m)d, k=%(k)d, b=%(b)d" % locals()
                    generate_class_A(b, 1, m, k, seed)
        print >> sys.stdout, "Collecting garbage"
        n = gc.collect()
        print >> sys.stdout, n, "Unreachable objects"

        # class B
        for m in action_intervals:
            for k in num_plans:
                for n in beh_proportions:
                    for p in failure_probs:
                        b = int(m * (1.0 + p)) * n
                        print >> sys.stdout, "Generating problem with parameters:"
                        print >> sys.stdout, "m=%(m)d, p=%(p)f, k=%(k)d, b=%(b)d" % locals()
                        # generate_class_B( b, 1, p, m, k, seed )
        print >> sys.stdout, "Collecting garbage"
        n = gc.collect()
        print >> sys.stdout, n, "Unreachable objects"


if __name__ == '__main__':
    main()
