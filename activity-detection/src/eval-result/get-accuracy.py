import sys
import os
lib_path = os.path.abspath('/home/dept/ta/yuhan/mobility-detector/src/Mobility-Detector/activity-detection/src/lib')
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

	#fh = open('full-accuracy','w')
	#path = '/home/dept/ta/yuhan/mobility-detector/kde_results/baseline_no_0.8_threshold/'
	#gnd_truth_file = path+'gnd_'+str(i)+'.plot'
	#classifier_file_avefv = path+'classifier_avefv_'+str(i)+'.plot'
	#classifier_file_avefv_ewma = path+'classifier_avefv_ewma_'+str(i)+'.plot'
	#classifier_file_avefv_hmm = path+'classifier_avefv_hmm_'+str(i)+'.plot'

	gnd_truth_output = read_output_file(gnd_truth_file)
	classifier_output = read_output_file(classifier_file)
	#classifier_avefv_output = read_output_file(classifier_file_avefv)
	#classifier_avefv_ewma_output = read_output_file(classifier_file_avefv_ewma)
	#classifier_avefv_hmm_output = read_output_file(classifier_file_avefv_hmm)

	sampling_intervals = ()
	statistics = Stats(gnd_truth_output, classifier_output, sampling_intervals, 'dummy', [4])
	#statistics_avefv_ewma = Stats(gnd_truth_output, classifier_avefv_ewma_output, sampling_intervals, 'dummy', [0,1,2,3,4])
	#statistics_avefv_hmm = Stats(gnd_truth_output, classifier_avefv_hmm_output, sampling_intervals, 'dummy', [0,1,2,3,4])
	print>> sys.stderr,"Hard match", statistics.match(match_type = 'hard')

	print>> sys.stderr,"Event based", statistics.event_match(match_type = 'event')
	'''	
		fh.write('\nfold ' + str(i) )
		fh.write('\n== bin-based ==')
		fh.write('\navefv:' + str(statistics_avefv.match(match_type = 'hard')))
		fh.write('\navefv+ewma:' + str(statistics_avefv_ewma.match(match_type = 'hard')))
		fh.write('\navefv+hmm:' + str(statistics_avefv_hmm.match(match_type = 'hard')))
		fh.write('\n\n== event-based ==')
		fh.write('\navefv')
		fh.write('\nrecall:' + str(statistics_avefv.event_match(match_type = 'event')['recall']))
		fh.write('\nprecision:' + str(statistics_avefv.event_match(match_type = 'event')['precision']))
		fh.write('\nlatency:' + str(statistics_avefv.event_match(match_type = 'event')['latency']))
		fh.write('\n\navefv+ewma')
		fh.write('\nrecall:' + str(statistics_avefv_ewma.event_match(match_type = 'event')['recall']))
		fh.write('\nprecision:'+ str(statistics_avefv_ewma.event_match(match_type = 'event')['precision']))
		fh.write('\nlatency:' + str(statistics_avefv_ewma.event_match(match_type = 'event')['latency']))
		fh.write('\n\navefv+hmm')
		fh.write('\nrecall:' + str(statistics_avefv_hmm.event_match(match_type = 'event')['recall']))
		fh.write('\nprecision:'+ str(statistics_avefv_hmm.event_match(match_type = 'event')['precision']))
		fh.write('\nlatency:'+ str(statistics_avefv_hmm.event_match(match_type = 'event')['latency']))
	'''
