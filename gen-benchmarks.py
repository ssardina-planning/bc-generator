import sys
import os

def main() :
	if len(sys.argv) != 2: 
		sys.exit("Please provide random seed")
		#sys.exit("Please provide the config file containing benchmark parameters.")

	seeds = []
	try :
		seeds.append( int(sys.argv[1]) )
	except ValueError :
		seeds_file = sys.argv[1]
		if not os.path.exists( seeds_file ) :
			print >> sys.stderr, "Input argument wasn't a seed (integer) nor a file with a list of seeds!"
			sys.exit(1)
		with open( seeds_file ) as instream :
			for line in instream :
				line = line.strip()
				if line[0] == '#' : continue
				try :
					seed = int(line)
					seeds.append(seed)
				except ValueError :
					print >> sys.stderr, line, "is not an integer number"
					sys.exit(1)

	for seed in seeds :
		os.system( 'python gen-ndp-task.py %s'%seed )
		os.system( 'python gen-ndp-tasks-IT.py %s'%seed )
		os.system( 'python gen-ndp-tasks-AU.py %s'%seed )

if __name__ == '__main__' :
	main()
