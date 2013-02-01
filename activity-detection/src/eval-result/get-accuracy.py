import sys
import os
lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)
from stats import *

def read_output_file(filename):
	output_list = []
	fh = open(filename,'r')
	for line in fh.readlines():
		pair = (int(line.split('\t')[0]),int(line.split('\t')[1]))
		output_list += [pair]

	return output_list

if __name__ == "__main__":
	if (len(sys.argv) < 3):
		print "Usage:", sys.argv[0],"gnd_truth.plot classifier.output"
		exit(5)
	
	gnd_truth_file = sys.argv[1]
	classifier_file = sys.argv[2]

	gnd_truth_output = read_output_file(gnd_truth_file)
	classifier_output  = read_output_file(classifier_file)
	print gnd_truth_output

	sampling_intervals = ()
	statistics = Stats(gnd_truth_output, classifier_output, sampling_intervals, 'dummy', [0,1,2,3,4])
	print>> sys.stderr,"Hard match", statistics.match(match_type = 'hard')

	print>> sys.stderr,"Event based", statistics.match(match_type = 'event')



