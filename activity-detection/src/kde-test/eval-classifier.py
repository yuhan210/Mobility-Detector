#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Use traces of arbitrary length to test the classifier.
'''
import sys
import os
lib_path = os.path.abspath('/home/dept/ta/yuhan/mobility-detector/src/Mobility-Detector/activity-detection/src/lib')
sys.path.append(lib_path)
from classifyKDEnSimpleEnergyAdaptive import *
from phone import *
from stats import *

if __name__ == "__main__" :
	if ( len(sys.argv) < 9 ) :
		print "Usage: ",sys.argv[0]," stitched_trace power_model callbacks(e.g:1-2-3) accel_classifier_model gsm_classifier_model wifi_classifier_model gps_classifier_model fold_num"
		exit(5)
	stitched_trace=sys.argv[1]
	power_model=sys.argv[2]
	callback_str = sys.argv[3]
	callback_list = map(lambda x : int(x),sys.argv[3].split("-"))
	accel_classifier_model = sys.argv[4]
	gsm_classifier_model = sys.argv[5]
	wifi_classifier_model = sys.argv[6]
	gps_classifier_model = sys.argv[7]
	fold_num = int(sys.argv[8])

	''' Initialize phone object '''
	sim_phone=Phone(stitched_trace)
	
	''' Initialize classifier object '''
	#classifier=DTClassify(sim_phone,power_model,callback_list)
	classifier = KernelSimpleEnergyClassify(sim_phone, accel_classifier_model, gsm_classifier_model, wifi_classifier_model, gps_classifier_model, power_model, callback_list)
	''' run classifier on phone '''
	sampling_rate_vector=sim_phone.run_classifier(classifier)
	
	''' print statistics '''
	statistics_combined=Stats(sim_phone.gnd_truth,classifier.classifier_output_combined,sampling_rate_vector,power_model,callback_list)
	statistics_combined_ewma=Stats(sim_phone.gnd_truth,classifier.classifier_output_combined_ewma,sampling_rate_vector,power_model,callback_list)
	statistics_combined_hmm=Stats(sim_phone.gnd_truth,classifier.classifier_output_combined_hmm,sampling_rate_vector,power_model,callback_list)
	
	statistics_accel_avefv=Stats(sim_phone.gnd_truth,classifier.classifier_output_avefv,sampling_rate_vector,power_model,callback_list)
	statistics_speed = Stats(sim_phone.gnd_truth,classifier.classifier_output_speed,sampling_rate_vector,power_model,callback_list)
	#statistics=Stats(sim_phone.gnd_truth,classifier.classifier_output,sampling_rate_vector,power_model)
	acc_fh=open("accuracy"+"_"+str(fold_num) + "_"+ callback_str + ".out","w")
	acc_fh.write("Hard match (accel+speed):"+str(statistics_combined.match(match_type='hard')) + "\n")
	acc_fh.write("Hard match (accel+speed+ewma):"+str(statistics_combined_ewma.match(match_type='hard')) + "\n")
	acc_fh.write("Hard match (acce+_speed+hmm):"+str(statistics_combined_hmm.match(match_type='hard'))+ "\n")
	acc_fh.write("Hard match (accel):"+str(statistics_accel_avefv.match(match_type='hard'))+ "\n")
	acc_fh.write("Hard match (speed):"+str(statistics_speed.match(match_type='hard'))+ "\n")
	#print>>sys.stderr,"Detection latency : \n -----------"
	#statistics.latency_stats()
	#print "Graph data :"
	fh=open("classifier_combined_"+str(fold_num)+"_"+ callback_str +".plot","w");
	for output in classifier.classifier_output_combined :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("classifier_combined_ewma_"+str(fold_num)+"_" + callback_str+".plot","w");
	for output in classifier.classifier_output_combined_ewma :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("classifier_combined_hmm_"+str(fold_num)+"_" + callback_str+ ".plot","w");
	for output in classifier.classifier_output_combined_hmm :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("gnd_"+str(fold_num)+ "_" + callback_str+ ".plot","w");
	for output in sim_phone.gnd_truth :
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("classifier_accel_"+str(fold_num)+ "_"+ callback_str+".plot","w");
	for output in classifier.classifier_output_avefv:
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("classifier_speed_"+str(fold_num)+"_" + callback_str+ ".plot","w");
	for output in classifier.classifier_output_speed:
		fh.write(str(output[0])+"\t"+str(output[1])+"\n");
	fh=open("fv_based_conf_matrix"+str(fold_num)+"_" + callback_str + ".out","w")
	for i in xrange(5):
		for j in xrange(5):
			fh.write(str(classifier.feature_based_conf_matrix[i][j]) + ",")
		fh.write("\n")
		
	total_fv_num = 0	
	correct_num = 0
	for i in xrange(5):
		total_fv_num += sum(classifier.feature_based_conf_matrix[i])
		correct_num += classifier.feature_based_conf_matrix[i][i]
	acc_fh.write("Feature vector based (accel):"+ str(float(correct_num)/total_fv_num)+"\n")
	acc_fh.write("Energy consumption:" + str(statistics_combined.energy_stats())+" Joules " + "\n")
