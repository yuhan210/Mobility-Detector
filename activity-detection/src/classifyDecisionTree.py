#! /usr/bin/python
from decisionTree import *
from sensors import *
from math import *
from numpy.fft import *
from location import *
import numpy
from normal import *
from distributions import *
import sys
import operator
# classify based on traces
class DTClassify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS=1000
	accel_current_window=[]
	gps_current_window=[]
	last_prediction_time = -1
	last_accel_update = -1
	last_gps_update = -1
	feature_vector = {}

	''' Energy adapataion '''
	last_energy_update=0  # assume that time starts from 0 in the stitched traces
	current_sampling_interval=1
	energy_consumed=0
	energy_budget=0

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()


	''' dhmm '''
	transition_prob = [[1,0.2,0.2,0.2,0.2],[0.2,1,0.1,0.2,0.1],[0.2,0.2,1,0.00000001,0.00000001],[0.2,0.00000001,0.00000001,1,0.00000001],[0.2,0.00000001,0.00000001,0.00000001,1]]
	state_score = [0.25] * 5
	def __init__(self,sim_phone, power_model, callback_list):
		self.sim_phone=sim_phone
		self.classifier_output_raw=[]
		self.classifier_output_hmm = []
		self.fh = open('test_feature.out','w')
		''' set initial sampling intervals in milliseconds '''
		self.current_sampling_interval=1
		sim_phone.change_accel_interval(31.25)
		sim_phone.change_gps_interval(1000)

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def callback(self,sensor_reading,current_time):
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (current_time - self.last_gps_update) >= 3 * 60 * 1000: # gps timeout
			self.classifier_output.append((current_time,-1))
			self.feature_vector['speed'] = -1

		if (isinstance(sensor_reading,GPS)):
			self.last_gps_update = current_time
			self.feature_vector['speed'] = sensor_reading.speed	
			

		if (isinstance(sensor_reading,Accel)):
			#print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.accel_current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.accel_current_window)
		        self.accel_current_window+=[(current_time,accel_mag)]


			self.last_accel_update = current_time if self.last_accel_update == -1 else self.last_accel_update
			if (current_time - self.last_accel_update) >= self.WINDOW_IN_MILLI_SECONDS:
				self.last_accel_update = current_time
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.accel_current_window));
				self.feature_vector['var'] = variance
				#print "Mean, sigma ",mean,sigma
				
				''' 1Hz - 3Hz coefficient '''
				hz1_mag = -1
				hz2_mag = -1
				hz3_mag = -1

				current_dft =rfft(map(lambda x: x[1], self.accel_current_window))
				if (len(current_dft) > 1):
					dft_coeff = numpy.abs(current_dft)

					N=float(len(self.accel_current_window))
					sampling_freq=N/((self.accel_current_window[-1][0]-self.accel_current_window[0][0])/1000.0)
					nyquist_freq = sampling_freq / 2.0
					if (len(current_dft) > int(ceil((3/(sampling_freq*1.0)) * N))):
						hz1_mag = dft_coeff[int(ceil((1/(sampling_freq * 1.0)) * N))]
						hz2_mag = dft_coeff[int(ceil((2/(sampling_freq * 1.0)) * N))]
						hz3_mag = dft_coeff[int(ceil((3/(sampling_freq * 1.0)) * N))]
				
					self.feature_vector['1hz'] = hz1_mag
					self.feature_vector['2hz'] = hz2_mag
					self.feature_vector['3hz'] = hz3_mag
							
					if self.feature_vector.has_key('speed'):
						if self.feature_vector['speed'] != -1:
							prediction = DecisionTree(self.feature_vector).classify()
							
							class_prob = [0.0] * 5
							class_prob[prediction] = 1.0
							
							new_state_score = [0]* 5
							for i in xrange(5):
								max_score = -1.0 * sys.float_info.max
								for j in xrange(5):
									transition_score = self.transition_prob[j][i]

									cand_score = self.state_score[j] + log(transition_score) + log(max(class_prob[i], 0.001))
									if cand_score > max_score:
										max_score = cand_score

								new_state_score[i] = max_score
							for i in xrange(5):
								self.state_score[i] = new_state_score[i]



							self.classifier_output_raw.append((current_time,prediction))
							self.classifier_output_hmm.append((current_time,self.state_score.index(max(self.state_score))))

							output_str = str(self.feature_vector['speed'])+',' + str(self.feature_vector['var']) +','+ str(self.feature_vector['1hz']) + ',' + str(self.feature_vector['2hz']) + ','+ str(self.feature_vector['3hz']) + ',' +  str(sensor_reading.gnd_truth) + '\n'
							self.fh.write(output_str)

					


