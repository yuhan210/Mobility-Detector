#! /usr/bin/python
# Indoor Outdoor classifier
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
import sys
import operator
# Train based on traces
class Train(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS=5000
	current_window=[]
	NUM_STATES=3

	''' Stats '''
	fraction_aps_list=dict()
	avg_rssi_list=dict()

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()

	def __init__(self,sim_phone,power_model) :
		self.sim_phone=sim_phone
		self.classifier_output=[]

		for i in range(0,self.NUM_STATES) :
			self.fraction_aps_list[i]=[]
			self.avg_rssi_list[i]=[]
		execfile(power_model)
		
		''' set initial sampling intervals in milliseconds to the lowest '''
		sim_phone.change_accel_interval(min(self.power_accel.keys()))
		sim_phone.change_wifi_interval(min(self.power_wifi.keys()))
		sim_phone.change_gps_interval(min(self.power_gps.keys()))
		sim_phone.change_gsm_interval(min(self.power_gsm.keys()))
		sim_phone.change_nwk_loc_interval(min(self.power_nwk_loc.keys()))
		
	def callback(self,sensor_reading,current_time,gnd_truth) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,WiFi)) :
			# zip aps and rssis into one list
			ap_rssis=zip(sensor_reading.ap_list,sensor_reading.rssi_list);
			self.current_window+=[(sensor_reading.time_stamp,ap_rssis)]
			self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
			
			# calc. num of aps in window :
			aps_seen=reduce(lambda acc,update : acc + len(update[1]),self.current_window,0)
		
			# calc. num of aps in window above threshold :
			threshold=-80
			good_ap_window=[]
			for sample in self.current_window :
				ts=sample[0]
				aps=sample[1]
				good_aps= filter(lambda x : x[1] > threshold,aps);
				good_ap_window+=[(ts,good_aps)]
			good_aps_seen=reduce(lambda acc,update : acc + len(update[1]),good_ap_window,0)
		
			# calculate average over sliding window :
			sum_window_rssi=0
			for sample in self.current_window :
				ts=sample[0]
				aps=sample[1]
				sum_window_rssi+= reduce(lambda acc,update : acc + update[1] ,aps ,0);
			avg_window_rssi=sum_window_rssi/aps_seen;
			fraction_good_aps=(good_aps_seen*1.0)/aps_seen
			if (gnd_truth != 0) : # Don't log unknown
				self.avg_rssi_list[gnd_truth]+=[avg_window_rssi]
				self.fraction_aps_list[gnd_truth]+=[fraction_good_aps]

	def output_classifer(self) :
		''' Print out any training relevant information to a file '''
		''' In this case, it is the mean and sigma for each distribution '''
		for i in range(0,self.NUM_STATES) : # all labels
			print>>sys.stderr,"self.avg_rssi_dist["+str(i)+"]=Normal("+str(Normal(self.avg_rssi_list[i]).mean)+","+str(Normal(self.avg_rssi_list[i]).sigma)+")"
			print>>sys.stderr,"self.fraction_aps_dist["+str(i)+"]=Normal("+str(Normal(self.fraction_aps_list[i]).mean)+","+str(Normal(self.fraction_aps_list[i]).sigma)+")"
