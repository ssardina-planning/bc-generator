#!/usr/bin/python
import sys
import os

def main() :
	dest = '.'
	if len(sys.argv) == 2 :
		dest = sys.argv[1]
		if not os.path.exists( dest ) :
			print >> sys.stderr, "Destination folder", dest, "does not exist"
			sys.exit(1)
	
	os.system( 'find . -name "*.tar.bz2" > filelist' )

	with open( 'filelist' ) as inputfiles :
		for line in inputfiles :
			line = line.strip()
			os.system( 'cp %s %s'%( line, dest ) )

	os.system( 'rm ../benchmarks/prp/class-A/*' )
	os.system( 'rm ../benchmarks/prp/class-C/*' )
	os.system( 'rm ../benchmarks/prp/class-I/*' )
	os.system( 'rm ../benchmarks/prp/class-T/*' )
	os.system( 'rm ../benchmarks/prp/class-AU/*' )

	os.system( 'mv problem-class-A-U-*.tar.bz2 ../benchmarks/prp/class-AU/' )
	os.system( 'mv problem-class-A-*.tar.bz2 ../benchmarks/prp/class-A/' )
	os.system( 'mv problem-class-I-*.tar.bz2 ../benchmarks/prp/class-I/' )
	os.system( 'mv problem-class-T-*.tar.bz2 ../benchmarks/prp/class-T/' )
	os.system( 'mv problem-class-C-*.tar.bz2 ../benchmarks/prp/class-C/' )
	
	os.system( 'find . -name "*.nugat.smv" > filelist' )

	with open( 'filelist' ) as inputfiles :
		for line in inputfiles :
			line = line.strip()
			os.system( 'cp %s %s'%( line, dest ) )

	os.system( 'find . -name "*.ispl" > filelist' )

	with open( 'filelist' ) as inputfiles :
		for line in inputfiles :
			line = line.strip()
			os.system( 'cp %s %s'%( line, dest ) )


	os.system( 'rm -rf filelist' )

if __name__ == '__main__' :
	main()
