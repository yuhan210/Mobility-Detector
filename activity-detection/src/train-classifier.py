#! /usr/bin/python 
''' Framework to evaluate classifiers on user generated traces.
    Use traces of arbitrary length to test the classifier.
'''
import sys
from trainIO import *
from phone import *
if __name__ == "__main__" :
	if ( len(sys.argv) < 7 ) :
		print "Usage: ",sys.argv[0]," accel-trace wifi-trace gps-trace gsm-trace nwk-loc-trace power_model "
		exit(5)
	accel_trace=sys.argv[1]
	wifi_trace=sys.argv[2]
	gps_trace=sys.argv[3]
	gsm_trace=sys.argv[4]
	nwk_loc_trace=sys.argv[5]	
	power_model=sys.argv[6]
	''' Initialize phone object '''
	sim_phone=Phone(accel_trace,wifi_trace,gps_trace,gsm_trace,nwk_loc_trace)
	''' Initialize classifier object '''
	trainer=Train(sim_phone,power_model)
	''' Now, train it ''' 
	sim_phone.run_trainer(trainer)
	''' Output classifier '''
	trainer.output_classifer()
