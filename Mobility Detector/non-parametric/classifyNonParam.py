#! /usr/bin/python
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
import sys
import operator
# classify based on traces
class NonParamClassify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS=5000
	current_window=[]
	last_print_out = -1

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()

	activity_templates=dict()	
	recs = dict()
	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
		self.classifier_output=[]
		
		''' set initial sampling intervals in milliseconds '''
		self.current_sampling_interval=(100)
		sim_phone.change_accel_interval(50)
		sim_phone.change_wifi_interval(60 * 1000)
		sim_phone.change_gps_interval(60 * 1000)
		sim_phone.change_gsm_interval(60 * 1000)
		sim_phone.change_nwk_loc_interval(60 * 1000)
		
		execfile("non_param_training_model",self.recs) #get activity_templates
		self.activity_templates = self.recs['activity_templates']
	
	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def predict_label(self, cur_window, detection_step = 5):
		gamma = 1
		# shifted detection
		prob = dict()

		for i in range(5):
			dist = []
			prob[i] = []
			for j in range(len(self.activity_templates[i])):
				dist.append(self.shifted_dist_func(cur_window,self.activity_templates[i][j], detection_step))
			prob[i]+= [numpy.mean([exp(-gamma * d) for d in dist])]

		return prob
		

	def shifted_dist_func(self,cur_window, template, detection_step):
		
		time_interval = cur_window[-1][0] - cur_window[0][0]
			
		dists = []
		for i in range(0,len(template),detection_step):
			for j in range(i+1,len(template)):
				if template[j][0] - template[i][0] >= time_interval:
					dists.append(self.dist_func(cur_window, template[i:j]))
					break

		return min(dists)

	def dist_func(self,cur_window,  segment):
	
		
		downsampled_segment = []
		downsampled_segment.append(segment[0])
		
		for i in range(1, len(cur_window)):
			time_diff = cur_window[i][0] - cur_window[0][0]
			minimum_time_dist = sys.maxint
			minimum_time_dist_index = -1
			for j in range(1, len(segment)):
				if abs((segment[j][0] - segment[0][0])-time_diff) < minimum_time_dist:
					minimum_time_dist = abs((segment[j][0] - segment[0][0])-time_diff)
					minimum_time_dist_index = j
			
			downsampled_segment.append(segment[minimum_time_dist_index])


		return sqrt(sum( [(downsampled_segment[i][1] - cur_window[i][1])** 2  for i in range(len(downsampled_segment))]))

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,Accel)) :
			#print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			start_time = self.current_window[0][0]

			posterior_prob = []
			if (current_time - self.last_print_out) >= self.WINDOW_IN_MILLI_SECONDS:
				#print self.current_window
				posterior_prob = self.predict_label(self.current_window)	
				self.last_print_out = current_time - self.WINDOW_IN_MILLI_SECONDS/2
				self.classifier_output.append((current_time, posterior_prob))

	def energy_adapt (self, current_time, energy_budget, total_time, power_accel, callback_list, posterior_pmf) :
			''' Vary sampling rate to adapt to energy constraints '''
			self.energy_consumed += (current_time-self.last_energy_update) * power_accel[self.current_sampling_interval]
			remaining_power=(energy_budget-self.energy_consumed)*1.0/(total_time-current_time)
			print "Current sampling interval is ",self.current_sampling_interval," remaining power is ",remaining_power," Joules per millisecond "
			# ramp down if required
			if (( power_accel[self.current_sampling_interval] > remaining_power)) :
				# pick the sampling interval with the max power which is less than remaining_power
				# items() returns a list of (key,value) tuples. Key is the sampling_interval. value is the power
				candidate_list = filter(lambda x : x[1] < remaining_power,power_accel.items())
				self.current_sampling_interval = max(candidate_list, key = lambda x : x[1])[0]
				self.sim_phone.change_accel_interval(self.current_sampling_interval)
				return
			# check if you can ramp up at all
			do_i_ramp_up=reduce(lambda acc, update : acc or (posterior_pmf[update] >= 0.2), callback_list ,False); 
			if (do_i_ramp_up) :
				min_interval=self.current_sampling_interval
				for candidate_interval in power_accel :
					if ((power_accel[candidate_interval] < remaining_power) and (candidate_interval < min_interval)) :
						min_interval=candidate_interval
				self.current_sampling_interval=min_interval;
				self.sim_phone.change_accel_interval(self.current_sampling_interval)
				return
