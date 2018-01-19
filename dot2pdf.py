import glob
import sys
import os

def main() :

	input_dir = sys.argv[1]
	dot_files = glob.glob( '%s/*.dot'%input_dir )
	for dot_file in dot_files :
		pdf_file = dot_file.replace('dot','pdf' )
		os.system( 'dot -Tpdf -o %s %s'%(pdf_file,dot_file) )

if __name__ == '__main__' :
	main()
