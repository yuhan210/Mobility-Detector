#! /usr/bin/python
# train based on traces
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
import sys
class  NonParametricTrain(object) :

	''' Windowing primitives '''
	last_print_out=-1
	WINDOW_IN_MILLI_SECONDS=5000
	current_window=[]
	

	''' Data required for ML estimates for each label '''
	''' Key to the hash table is the label number '''
	#mean_stats=dict()
	#sigma_stats=dict()
	#peak_freq_stats=dict()
	#strength_var_stats=dict()

	activity_templates =dict()


	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
		for i in range(5):
			self.activity_templates[i]=[]

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def spike_normalization(self, value_list):
		ALPHA = 1.2
		if (value_list==[]):
			return (None)
		w_smoothed = []
		for i in range(0,len(value_list)):
			if i == 0:
				w_smoothed.append(0)
			else:
				w_smoothed.append(abs(value_list[i]-valule_list[i-1])** ALPHA )
		
		return w_smoothed 


	def callback(self,sensor_reading,current_time,gnd_truth) :
		if (isinstance(sensor_reading,Accel)) :
			
		
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS * 2,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			startTime = self.current_window[0][0]
			
			template = map(lambda x: ((x[0]-startTime),x[1]), self.current_window);
			if len(self.activity_templates[gnd_truth]) == 0:
				if template[-1][0] >= self.WINDOW_IN_MILLI_SECONDS * 2:
					self.last_print_out = current_time
					self.activity_templates[gnd_truth] += [template]

			else:
				if (current_time - self.last_print_out)  >= self.WINDOW_IN_MILLI_SECONDS: 
					self.last_print_out = current_time
					self.activity_templates[gnd_truth] += [template]

			

			''' get spike-normalized window '''
			#w_smoothed = self.spike_normalization(map(lambda x: x[1], self.current_window));
				
		
	def output_classifer(self) :

		# make sure each activity has the same number of templates
		minimum_template_num = min(map(lambda x: len(self.activity_templates[x]), self.activity_templates))
		
		for i in range(5):
			while len(self.activity_templates[i]) > minimum_template_num:
				self.activity_templates[i].pop(0)	

		
		print "activity_templates = ",self.activity_templates
