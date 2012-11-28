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

	activity_templates=[]	
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

	def predict_label(self, observed_signal, detection_step = 5):
		gamma = 1
		# shifted detection
		prob = []

		for i in range(5):
			dist = []
			prob[i] = 0
			for j in range(len(self.activity_templates[i])):
				dist.append(self.shifted_dist_func(observed_signal,self.activity_templates[i][j], detection_step))
			prob[i] = numpy.sum([exp(-gamma * d) for d in dist])

		return prob
		

	def shifted_dist_func(self, cur_window, template, detection_step):
		
		time_interval = cur_window[-1][0] - cur_window[0][0]
			
		dists = []
		for i in range(0,len(template),detection_step): # sweep through template
			for j in range(i+1,len(template)):    # find right end point of current candidate
				if template[j][0] - template[i][0] >= time_interval:
					dists.append(self.dist_func(cur_window, template[i:j]))
					break
		# return best match
		return min(dists)

	def dist_func(self, cur_window,  segment):
	
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

		downsampled_signal=numpy.array(map(lambda x : x[1],downsampled_segment))
		cur_window_signal=numpy.array(map(lambda x : x[1], cur_window))
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
			if (current_time - self.last_print_out) >= self.WINDOW_IN_MILLI_SECONDS/2.0 :
				#print self.current_window
				posterior_prob = self.predict_label(self.current_window)	
				self.last_print_out = current_time
				self.classifier_output.append((current_time, posterior_prob))
