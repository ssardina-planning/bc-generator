#!/usr/bin/python
"""
This software generates behavior composition problems (behaviors + target) for experimenation.

It outputs .dot files for each module.

In general it generates behaviors from a configuration file, then does the cross product and extracts a deterministic
fragment out of it to build the target.
"""
import sys, os
from bc.generator import Problem_Generator
from helper import utilities


'''
NOTE: This software was done in 20010 and then extended in 2013 with Python 2.7 and networkx 1.0.

I have migrated to the new networkx 2.0, but there were big changes when moving from networkx 1.0 to 2.0:

https://networkx.github.io/documentation/stable/release/migration_guide_from_1.x_to_2.0.html

With the release of NetworkX 2.0 we are moving to a view/iterator reporting API. We have moved many methods from 
reporting lists or dicts to iterating over the information. 

1. replace nx.draw($1, pos=graphviz_layout($1)) with nx.draw($1, pos=graphviz_layout($1))
2. changed all x.nodes_iter() and x.edges_iter() to x.nodes and x.edges
3. replaced x.nodes()[0] with list(x.nodes)[0]
'''


def main():
    # check if config file name passed as argument
    if len(sys.argv) != 2:
        sys.exit("Please provide the config file containing benchmark parameters.")

    configfile = sys.argv[1]

    # check if file exists
    if not os.path.isfile(configfile):
        sys.exit("Config file not found.")

    # load the config for composition benchmark to be generated
    config = utilities.read_config(configfile)
    prob_gen = Problem_Generator(config)
    prob_gen.generate_behaviors()
    prob_gen.compute_target()


if __name__ == '__main__':
    main()
