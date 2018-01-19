#!/usr/bin/python
import sys, os
from bc.generator import Problem_Generator
from helper import utilities

def main() :
	#check if config file name passed as argument
	if len(sys.argv) != 2: 
		sys.exit("Please provide the config file containing benchmark parameters.")

	configfile = sys.argv[1]

	#check if file exists
	if not os.path.isfile(configfile):
		sys.exit("Config file not found.")

	#load the config for composition benchmark to be generated
	config = utilities.read_config(configfile)
	prob_gen = Problem_Generator( config )
	prob_gen.generate_behaviors()
	prob_gen.compute_target()
	
if __name__ == '__main__' :
	main()
