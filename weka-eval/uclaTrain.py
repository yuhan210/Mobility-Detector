#! /usr/bin/python
# train based on traces
from sensors import *
from math import *
from numpy.fft import *
import numpy
import sys
class uclaTrain(object) :

	''' Windowing primitives '''
	last_print_out=-1
	WINDOW_IN_MILLI_SECONDS=1000
	current_window=[]

	cur_accel_feature = {}

	def __init__(self,sim_phone, arff_file) :
		self.sim_phone=sim_phone
		self.arff_file = arff_file

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def callback(self,sensor_reading,current_time,gnd_truth) :
		if (isinstance(sensor_reading, GPS)):
			feature_str = ""
			if (self.cur_accel_feature.has_key('var') and self.cur_accel_feature.has_key('1Hz') and self.cur_accel_feature.has_key('2Hz') and self.cur_accel_feature.has_key('3Hz')):
				if (gnd_truth == 3 or gnd_truth == 4):
					if (sensor_reading.speed) > 1.0:
						feature_str = str(sensor_reading.speed) + ","+str(self.cur_accel_feature['var']) + "," + str(self.cur_accel_feature['1Hz']) + "," + str(self.cur_accel_feature['2Hz']) + "," + str(self.cur_accel_feature['3Hz'])+ ","+ str(gnd_truth) + "\n"
						self.arff_file.write(feature_str)	
				else:
					feature_str = str(sensor_reading.speed) + ","+str(self.cur_accel_feature['var']) + "," + str(self.cur_accel_feature['1Hz']) + "," + str(self.cur_accel_feature['2Hz']) + "," + str(self.cur_accel_feature['3Hz'])+ ","+ str(gnd_truth) + "\n"
					self.arff_file.write(feature_str)	

		if (isinstance(sensor_reading,Accel)) :
			#print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]

			self.last_print_out = current_time if self.last_print_out == -1 else self.last_print_out
			self.cur_accel_feature = {}
			if (current_time - self.last_print_out) >= self.WINDOW_IN_MILLI_SECONDS:
				self.cur_accel_feature['gnd_truth'] = gnd_truth
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
				self.cur_accel_feature['var'] = variance
				sigma=sqrt(variance)


				''' 1Hz - 3Hz coefficient '''
				current_dft =rfft(map(lambda x: x[1], self.current_window))
				if (len(current_dft) > 1):
					dft_coeff = numpy.abs(current_dft)
					N=float(len(self.current_window))
					sampling_freq=N/((self.current_window[-1][0]-self.current_window[0][0])/1000.0)
					if (len(current_dft) > int(ceil((3/(sampling_freq*1.0)) * N))):
					#	print '1Hz index', int(ceil((1/(sampling_freq*1.0))* N))
					#	print '2Hz index', int(ceil((2/(sampling_freq*1.0))* N))
					#	print '3Hz index', int(ceil((3/(sampling_freq*1.0))* N))
						self.cur_accel_feature['1Hz'] = dft_coeff[int(ceil((1/(sampling_freq * 1.0)) * N))]
						self.cur_accel_feature['2Hz'] = dft_coeff[int(ceil((2/(sampling_freq * 1.0)) * N))]
						self.cur_accel_feature['3Hz'] = dft_coeff[int(ceil((3/(sampling_freq * 1.0)) * N))]



	def output_classifer(self) :

		self.arff_file.close()
