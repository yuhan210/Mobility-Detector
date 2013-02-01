#! /usr/bin/python

import sys
import os
lib_path = os.path.abspath('../lib')
sys.path.append(lib_path)
from sensors import *
from location import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
import operator
import pickle
from scipy.stats.kde import gaussian_kde
from scipy.stats import norm
#import matplotlib
# classify based on traces
class KernelSimpleEnergyClassify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS = 5000
	WIFI_WINDOW_IN_MILLI_SECONDS= (3 * 60 * 1000)
	GSM_WINDOW_IN_MILLI_SECONDS = (3 * 60 * 1000)
	GPS_WINDOW_IN_MILLI_SECONDS = (3 * 60 * 1000)


	wifi_distribution=[0]*5 
	gps_distribution = [0]*5
	prev_gps_pred = -1

	prev_bin = -1
	current_accel_fv = []
	current_wifi_fv = []

	current_accel_prediction = []
	current_window=[]
	current_wifi_obs=[]
	current_gps_obs=[]
	current_gps_obs=[]
	last_print_out = -1


	last_energy_update = 0
	activity_templates=[]	
	recs = dict()

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()
	energy_consumed=0
	current_sampling_interval = 1

	feature_list = []
	kernel_function = dict()
	callback_list = []
	#Viterbi
	#stateScore = [0]*5
	prev_prediction = -1
	#EWMA
	ewma_window = []

	''' dhmm '''
	transition_prob = [[1,0.2,0.2,0.2,0.2],[0.2,1,0.1,0.2,0.1],[0.2,0.2,1,0.00000001,0.00000001],[0.2,0.00000001,0.00000001,1,0.00000001],[0.2,0.00000001,0.00000001,0.00000001,1]]
	state_score = [0.2] * 5
	def __init__(self,sim_phone, classifier_model, power_model, callback_list) :
		self.sim_phone=sim_phone
		self.classifier_output_avefv=[]
		self.classifier_output_avefv_ewma=[]
		self.classifier_output_avefv_hmm=[]
		self.classifier_output_prediction=[]
		self.callback_list = callback_list
		self.ewma_window = [0.2]*5

		''' set initial sampling intervals in milliseconds '''
		self.current_sampling_interval = 1
		sim_phone.change_accel_interval(1)
		#self.current_sampling_interval=max(self.power_accel.keys())
		#sim_phone.change_accel_interval(max(self.power_accel.keys()))
		#sim_phone.change_gsm_interval(1000)
		#sim_phone.change_nwk_loc_interval(1000)
	
		''' load kde model '''
		classifier_model_handle=open(classifier_model,"r");
		self.training_feature_list = pickle.load(classifier_model_handle);
		for i in xrange(5):
			self.kernel_function[i] = []
			for j in xrange(len(self.training_feature_list[i])):
				kernel_pdf = gaussian_kde(self.training_feature_list[i][j])
				#kernel_pdf.covariance_factor = lambda : 0.
				#kernel_pdf._compute_covariance()
				self.kernel_function[i] += [kernel_pdf]
		self.training_feature_list = []

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def predict_label(self,mean_fv,sigma_fv,peak_freq_fv,strength_var_fv) :
		''' Predict the label given the mean, sigma, peak frequency and strength variation components of the feature vector '''
		likelihood=[sys.float_info.min]*5
		for label in xrange(5):
			likelihood[label] += (self.kernel_function[label][0].evaluate(mean_fv)[0]) * (self.kernel_function[label][1].evaluate(sigma_fv)[0]) *(self.kernel_function[label][2].evaluate(peak_freq_fv)[0]) * (self.kernel_function[label][3].evaluate(strength_var_fv)[0])
		
		posterior_pmf = [0]*5
		for label in xrange(5):
			if sum(likelihood) > 0:
				posterior_pmf[label]=likelihood[label]/(sum(likelihood)*1.0)
			else:
				posterior_pmf[label] = 0.2
				
		return	Distribution(5,posterior_pmf)


	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			start_time = self.current_window[0][0]

			self.last_print_out=current_time if self.last_print_out == -1 else self.last_print_out
			if (current_time - self.last_print_out) >= self.WINDOW_IN_MILLI_SECONDS : #compute a feature vector
				self.last_print_out = current_time	
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.current_window));
				sigma=sqrt(variance)
				#print "Mean, sigma ",mean,sigma

				''' Peak frequency, compute DFT first on accel magnitudes '''
				current_dft=rfft(map(lambda x : x[1] , self.current_window))
				peak_freq=0 # TODO Find a better way of doing this.
				if (len(current_dft) > 1) :
					''' ignore DC component '''
					peak_freq_index=numpy.abs(current_dft[1:]).argmax() + 1;
					''' sampling_frequency '''
					N=float(len(self.current_window))
					sampling_freq=N/(self.current_window[-1][0]-self.current_window[0][0])
					peak_freq=((peak_freq_index)/(N* 1.0)) * sampling_freq
					nyquist_freq=sampling_freq/2.0;
					assert ( peak_freq <= nyquist_freq );
					#print "Peak_freq ",peak_freq," Hz"

				''' Strength variation '''
				summits=[]
				valleys=[]
				sigma_summit=0
				sigma_valley=0
				for i in range(1,len(self.current_window)-1) :
					if ( (self.current_window[i][1] >= self.current_window[i+1][1]) and (self.current_window[i][1] >= self.current_window[i-1][1]) ) :
						summits+=[self.current_window[i]]
					if ( (self.current_window[i][1] <= self.current_window[i+1][1]) and (self.current_window[i][1] <= self.current_window[i-1][1]) ) :
						valleys+=[self.current_window[i]]
				if ( len(summits) != 0 ) :

					if self.mean_and_var(map(lambda x: x[1], summits))[1] > 0:
						sigma_summit=sqrt(self.mean_and_var(map(lambda x : x[1],summits))[1]);
				if ( len(valleys) != 0 ) :
					if self.mean_and_var(map(lambda x: x[1], valleys))[1] > 0:
						sigma_valley=sqrt(self.mean_and_var(map(lambda x : x[1],valleys))[1]);
				#print "Strength variation ", sigma_valley+sigma_summit
				posterior_dist=self.predict_label(mean,sigma,peak_freq,sigma_valley+sigma_summit)
		        	self.current_accel_prediction+= [(current_time,posterior_dist.mode())]
				self.current_accel_fv+=[(current_time,mean,sigma,peak_freq,sigma_valley+sigma_summit)]
				
				# Arbitrary values for unit test :
				#self.simple_energy_adapt(current_time, self.power_accel, self.callback_list, posterior_dist.pmf)
				#self.last_energy_update=current_time

		bin_size = 60 * 1000
		cur_bin = current_time/bin_size
			
	        self.prev_bin = cur_bin if self.prev_bin == -1 else self.prev_bin	 
		if cur_bin > self.prev_bin: # time to make a prediction
			self.prev_bin = cur_bin

			## accel
			self.current_accel_fv = filter(lambda x: x[0] >= current_time - bin_size, self.current_accel_fv)	
			self.current_accel_prediction = filter(lambda x: x[0] >= current_time - bin_size, self.current_accel_prediction)
 
			## prediction
			prediction_list = [0]*5
			for prediction_tuple in self.current_accel_prediction:
				prediction_list[prediction_tuple[1]] += 1				
		
			accel_likelihood_pred= [0] *5
			if sum(prediction_list) > 0:
				for i in xrange(5):
					accel_likelihood_pred[i] = prediction_list[i]/(sum(prediction_list)*1.0) 
			else:
				for i in xrange(5):
					accel_likelihood_pred[i] = 0.2
			##

			## ave_feature_vector
		   	accel_mean_list = []
			accel_std_list = []
			accel_pf_list = []
			accel_sv_list = []
			for accel_tuple in self.current_accel_fv:
				for i in xrange(1,len(accel_tuple)):
					if i == 1:
						accel_mean_list.append(accel_tuple[i])
					elif i == 2:
						accel_std_list.append(accel_tuple[i])
					elif i == 3:
						accel_pf_list.append(accel_tuple[i])
					elif i == 4:
						accel_sv_list.append(accel_tuple[i])
			(ave_fv_mean,dummy) = self.mean_and_var(accel_mean_list)
			(ave_fv_std,dummy) = self.mean_and_var(accel_std_list)
			(ave_fv_pf,dummy) = self.mean_and_var(accel_pf_list)
			(ave_fv_sv,dummy) = self.mean_and_var(accel_sv_list)
			
			accel_likelihood_avefv=self.predict_label(ave_fv_mean,ave_fv_std,ave_fv_pf,ave_fv_sv).pmf
		
			#if max(accel_likelihood_avefv) > 0.8:
			if True:
				self.classifier_output_avefv.append((current_time, accel_likelihood_avefv.index(max(accel_likelihood_avefv))))
				
				##EWMA
				current_prediction = accel_likelihood_avefv.index(max(accel_likelihood_avefv))
				ALPHA = 0.2
				Yt = [0] * 5
				Yt[current_prediction] = 1
				for i in xrange(5):
					self.ewma_window[i] = ALPHA * Yt[i] + (1-ALPHA) * self.ewma_window[i]

				self.classifier_output_avefv_ewma.append((current_time,self.ewma_window.index(max(self.ewma_window))))

				#HMM
				class_prob = [0.0] * 5
				class_prob[current_prediction] = 1.0
							
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
				
				self.classifier_output_avefv_hmm.append((current_time,self.state_score.index(max(self.state_score))))

			if True:
			#if max(accel_likelihood_pred) > 0.8:
				self.classifier_output_prediction.append((current_time, accel_likelihood_pred.index(max(accel_likelihood_pred))))

	def simple_energy_adapt(self, current_time, power_accel, callback_list, posterior_pmf):
			''' Vary sampling rate if confidence > 0.2'''
			self.energy_consumed += (current_time-self.last_energy_update) * power_accel[self.current_sampling_interval]
			#print "Current sampling interval is ",self.current_sampling_interval
			
			#ramp up if required
			#do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2) and (posterior_pmf[update]<=0.8)), callback_list ,False); 
			do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2)), callback_list ,False); 
			if (do_i_ramp_up):
				candidate_interval = filter(lambda x : x < self.current_sampling_interval,power_accel)
				if len(candidate_interval) > 0:
					self.current_sampling_interval = max(candidate_interval)
					self.sim_phone.change_accel_interval(self.current_sampling_interval)
				return
			else:
				candidate_interval = filter(lambda x : x > self.current_sampling_interval,power_accel)
				if len(candidate_interval) > 0:
					self.current_sampling_interval = min(candidate_interval)
					self.sim_phone.change_accel_interval(self.current_sampling_interval)
				return
