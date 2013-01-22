#! /usr/bin/python 
'''
It generates the feature file for the specified folder
'''
import sys
from train import *
import os
from phone import *
if __name__ == "__main__" :
	if ( len(sys.argv) < 4 ) :
		print "Usage: ",sys.argv[0]," path_to_data folder_num output_arff_name"
		exit(5)

	path_to_data=sys.argv[1]
	folder_num=sys.argv[2]
	arff_filename=sys.argv[3]
	arff_file = open(arff_filename,"w")

	#arff_file.write('@RELATION mode\n\n')
	#arff_file.write('@ATTRIBUTE speed NUMERIC\n')
	#arff_file.write('@ATTRIBUTE var NUMERIC\n')
	#arff_file.write('@ATTRIBUTE 1hz NUMERIC\n')
	#arff_file.write('@ATTRIBUTE 2hz NUMERIC\n')
	#arff_file.write('@ATTRIBUTE 3hz NUMERIC\n')
	#arff_file.write('@ATTRIBUTE gnd_truth {0,1,2,3,4}\n')
	#arff_file.write('\n@DATA\n')
	
	''' Initialize phone object '''
	activity_listing = os.listdir(path_to_data+"/"+folder_num)
	for activity in activity_listing:
		trace_listing = os.listdir(path_to_data+"/"+folder_num+"/"+activity)
		for trace in trace_listing:
			sim_phone = None
			trainer = None

			trace_path = path_to_data+"/"+folder_num+"/"+activity+"/"+trace
			print trace_path
			
			sensor_files = os.listdir(trace_path)
			dummy_file = "./dummy_file"
			accel_trace = dummy_file
			wifi_trace = dummy_file
			gps_trace = dummy_file
			gsm_trace = dummy_file
			nwk_loc_trace = dummy_file
					
			for sensor_file in sensor_files:
				if sensor_file.find("Accel")>=0:
					accel_trace = trace_path +"/"+ sensor_file
				elif sensor_file.find("GPS") >= 0:
					gps_trace = trace_path +"/"+ sensor_file
				elif sensor_file.find("Wifi") >= 0:
					wifi_trace = trace_path +"/"+ sensor_file
				elif sensor_file.find("Geo") >= 0:
					nwk_loc_trace = trace_path +"/"+ sensor_file
				elif sensor_file.find("GSM") >= 0:
					gsm_trace = trace_path +"/"+ sensor_file
					
			sim_phone=Phone(accel_trace,wifi_trace,gps_trace,gsm_trace,nwk_loc_trace)
			''' Initialize classifier object '''
			trainer=Train(sim_phone,arff_file)
			''' Now, train it ''' 
			sim_phone.run_trainer(trainer)
	''' Output classifier '''
	arff_file.close()
