#! /usr/bin/python
# train based on traces
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
import sys
class  Train(object) :

	''' Windowing primitives '''
	last_print_out=-1
	WINDOW_IN_MILLI_SECONDS=5000
	current_window=[]
	
	''' Data required for ML estimates for each label '''
	''' Key to the hash table is the label number '''
	activity_templates = [[]]*5

	def __init__(self,sim_phone) :
		self.sim_phone=sim_phone
	
	def callback(self,sensor_reading,current_time,gnd_truth) :

		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS * 2,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			startTime = self.current_window[0][0]
			template = map(lambda x: ((x[0]-startTime),x[1]), self.current_window);
			self.last_print_out=current_time if self.last_print_out == -1 else self.last_print_out
			if (current_time - self.last_print_out)  >= self.WINDOW_IN_MILLI_SECONDS: 
				self.last_print_out = current_time
				self.activity_templates[gnd_truth] += [template]

	def output_classifer(self) :

		# make sure each activity has the same number of templates
		minimum_template_num = min(map(lambda x: len(x), self.activity_templates))
		for i in range(5):
			while len(self.activity_templates[i]) > minimum_template_num:
				self.activity_templates[i].pop(0)	
		print "activity_templates = ",self.activity_templates
