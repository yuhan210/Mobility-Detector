#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Use traces of arbitrary length to test the classifier.
'''
import sys
#from classify import *
#from classifyNonParam import *
#from classifyIO import *
from classifyDecisionTree import *
from statsCallbacks import *
from phone import *
from stats import *
if __name__ == "__main__" :
	if ( len(sys.argv) < 4 ) :
		print "Usage: ",sys.argv[0]," stitched_trace power_model callbacks(e.g:1-2-3)"
		exit(5)
	stitched_trace=sys.argv[1]
	power_model=sys.argv[2]
	callback_list = map(lambda x : int(x),sys.argv[3].split("-"))

	''' Initialize phone object '''
	sim_phone=Phone(stitched_trace)
	
	
	''' Initialize classifier object '''
	classifier=DTClassify(sim_phone,power_model,callback_list)
	

	''' run classifier on phone '''
	sampling_rate_vector=sim_phone.run_classifier(classifier)
	
	
	''' print statistics '''
	print classifier.classifier_output
	statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model,callback_list)
	#statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model)
	print>>sys.stderr,"Hard match ",statistics.match(match_type='hard')
	#print>>sys.stderr,"Soft match ",statistics.match(match_type='soft')
	print>>sys.stderr,"Detection latency : \n -----------"
	#statistics.latency_stats()
	print "Graph data :"
	fh=open("classifier.plot","w");
	for output in classifier.classifier_output :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("gnd.plot","w");
	for output in sim_phone.gnd_truth :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	#print>>sys.stderr,"Energy consumption ",statistics.energy_stats()," Joules ";
