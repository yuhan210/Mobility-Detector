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
	accel_arff_file = open(arff_filename+"_accel.arff","w")
	gps_arff_file = open(arff_filename+"_gps.arff","w")
	wifi_arff_file = open(arff_filename+"_wifi.arff","w")
	gsm_arff_file = open(arff_filename+"_gsm.arff","w")

	
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
			trainer=Train(sim_phone,accel_arff_file,gps_arff_file,wifi_arff_file,gsm_arff_file)
			''' Now, train it ''' 
			sim_phone.run_trainer(trainer)
	''' Output classifier '''
	accel_arff_file.close()
	gps_arff_file.close()
	wifi_arff_file.close()
	gsm_arff_file.close()
