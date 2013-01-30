#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Use traces of arbitrary length to test the classifier.
'''
import sys
from classifyKDEnSimpleEnergyAdaptive import *
from statsCallbacks import *
from phone import *
from stats import *

if __name__ == "__main__" :
	if ( len(sys.argv) < 6 ) :
		print "Usage: ",sys.argv[0]," stitched_trace power_model callbacks(e.g:1-2-3) classifier_model fold_num"
		exit(5)
	stitched_trace=sys.argv[1]
	power_model=sys.argv[2]
	callback_list = map(lambda x : int(x),sys.argv[3].split("-"))
	classifier_model = sys.argv[4]
	fold_num = int(sys.argv[5])

	''' Initialize phone object '''
	sim_phone=Phone(stitched_trace)
	
	
	''' Initialize classifier object '''
	#classifier=DTClassify(sim_phone,power_model,callback_list)
	classifier = KernelSimpleEnergyClassify(sim_phone, classifier_model, power_model, callback_list)
	''' run classifier on phone '''
	sampling_rate_vector=sim_phone.run_classifier(classifier)
	
	''' print statistics '''
	statistics_avefv=Stats(sim_phone.gnd_truth,classifier.classifier_output_avefv,sampling_rate_vector,power_model,callback_list)
	statistics_prediction=Stats(sim_phone.gnd_truth,classifier.classifier_output_prediction,sampling_rate_vector,power_model,callback_list)

	#statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model)
	print>>sys.stderr,"Hard match ",statistics_avefv.match(match_type='hard')
	#print>>sys.stderr,"Soft match ",statistics.match(match_type='soft')
	print>>sys.stderr,"Detection latency : \n -----------"
	#statistics.latency_stats()
	print "Graph data :"
	fh=open("classifier_avefv_"+str(fold_num)+".plot","w");
	for output in classifier.classifier_output_avefv :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("gnd_"+str(fold_num)+".plot","w");
	for output in sim_phone.gnd_truth :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	#print>>sys.stderr,"Energy consumption ",statistics.energy_stats()," Joules ";
	#statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model)
	print>>sys.stderr,"Hard match ",statistics_prediction.match(match_type='hard')
	#print>>sys.stderr,"Soft match ",statistics.match(match_type='soft')
	print>>sys.stderr,"Detection latency : \n -----------"
	#statistics.latency_stats()
	print "Graph data :"
	fh=open("classifier_prediction_"+str(fold_num)+".plot","w");
	for output in classifier.classifier_output_prediction:
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
