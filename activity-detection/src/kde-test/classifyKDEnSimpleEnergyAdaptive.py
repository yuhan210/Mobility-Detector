#! /usr/bin/python

import sys
import os
lib_path = os.path.abspath('/home/dept/ta/yuhan/mobility-detector/src/Mobility-Detector/activity-detection/src/lib')
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
from scipy import stats
from scipy.stats import norm
#import matplotlib
# classify based on traces
class KernelSimpleEnergyClassify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS = 5000
	WIFI_WINDOW_IN_MILLI_SECONDS= (3 * 60 * 1000)
	GSM_WINDOW_IN_MILLI_SECONDS = (3 * 60 * 1000)
	GPS_WINDOW_IN_MILLI_SECONDS = (3 * 60 * 1000)


	prev_bin = -1
	current_accel_fv = []

	current_accel_prediction = []
	current_window=[]
	wifi_current_window = []
	gps_current_window = []
	gsm_current_window = []
	last_print_out = -1


	last_accel_energy_update = 0
	last_speed_energy_update = 0
	activity_templates=[]	
	recs = dict()

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()
	
	current_accel_sampling_interval = sys.maxint
	current_wifi_sampling_interval = sys.maxint
	current_gps_sampling_interval = sys.maxint
	current_gsm_sampling_interval = sys.maxint

	energy_consumed = 0

	feature_based_conf_matrix = [[ 0 for i in xrange(5)] for j in xrange(5)]
	feature_list = []
	accel_kernel_function = {}
	gsm_kernel_function = {}
	wifi_kernel_function = {}

	callback_list = []
	#Viterbi
	#stateScore = [0]*5
	prev_prediction = -1
	#EWMA
	ewma_window = []

	''' dhmm '''
	transition_prob = [[1,0.2,0.2,0.2,0.2],[0.2,1,0.1,0.2,0.1],[0.2,0.2,1,0.00000001,0.00000001],[0.2,0.00000001,0.00000001,1,0.00000001],[0.2,0.00000001,0.00000001,0.00000001,1]]
	state_score = [0.2] * 5
	def __init__(self,sim_phone, accel_classifier_model, gsm_classifier_model, wifi_classifier_model, gps_classifier_model , power_model, callback_list) :
		self.sim_phone=sim_phone
		self.classifier_output_combined=[]
		self.classifier_output_combined_ewma=[]
		self.classifier_output_combined_hmm=[]
		self.classifier_output_avefv=[]
		self.classifier_output_speed = []
		self.callback_list = callback_list
		self.ewma_window = [0.2]*5
		execfile(power_model)

		''' set initial sampling intervals in milliseconds '''
		self.sim_phone.change_gsm_interval(60 * 1000)
		self.sim_phone.change_wifi_interval(max(self.power_wifi.keys()))
		self.sim_phone.change_gps_interval(max(self.power_gps.keys()))
	
		self.current_gsm_sampling_interval = 60 * 1000 
		self.current_wifi_sampling_interval = max(self.power_wifi.keys())
		self.current_gps_sampling_interval = max(self.power_gps.keys())

		sim_phone.change_accel_interval(max(self.power_accel.keys()))
		self.current_accel_sampling_interval=max(self.power_accel.keys())
			
		''' load model '''
		self.accel_kernel_function = self.load_accel_model(accel_classifier_model)
		self.gsm_kernel_function = self.load_cell_model(gsm_classifier_model)
		self.wifi_kernel_function = self.load_cell_model(wifi_classifier_model)

	def load_accel_model(self, accel_classifier_model):
		classifier_model_handle=open(accel_classifier_model,"r")
		training_feature_list = pickle.load(classifier_model_handle)
		kernel_function = {}
		for i in xrange(5):
			kernel_function[i] = []
			for j in xrange(len(training_feature_list[i])):
				
				kernel_pdf = stats.gaussian_kde(training_feature_list[i][j])
				kernel_pdf.set_bandwidth(bw_method = 0.05)
				#setattr(kernel_pdf, 'self.covariance_factor', self.covariance_factor.__get__(kernel_pdf, type(kernel_pdf)))
				#kernel_pdf._compute_covariance()
				kernel_function[i] += [kernel_pdf]

		training_feature_list = []
		classifier_model_handle.close()

		return kernel_function

	def load_cell_model(self, cell_classifier_model):
		common_cell_ratio_stats = {}
		rssi_dist_ratio_stats = {}
		for i in xrange(5):
			common_cell_ratio_stats[i] = []
			rssi_dist_ratio_stats[i] = []

		classifier_model_handle = open(cell_classifier_model, 'r')
		for line in classifier_model_handle.readlines():
			common_cell_ratio = float(line.split(',')[0])
			rssi_dist_ratio = float(line.split(',')[1])
			gnd_truth = int(line.split(',')[-1])

			common_cell_ratio_stats[gnd_truth] += [common_cell_ratio]
			rssi_dist_ratio_stats[gnd_truth] += [rssi_dist_ratio]

		output_fv_dict= {}
		for i in xrange(5):
			output_fv_dict[i] = []
			output_fv_dict[i] += [common_cell_ratio_stats[i]] # a list
			output_fv_dict[i] += [rssi_dist_ratio_stats[i]]

		cell_kernel_function = {}
		for i in xrange(5):
			cell_kernel_function[i] = []
			for j in xrange(len(output_fv_dict[i])):
				
				kernel_pdf = gaussian_kde(output_fv_dict[i][j])
				if j == 0:
					kernel_pdf.set_bandwidth(bw_method = 0.1)
				if j == 1:
					kernel_pdf.set_bandwidth(bw_method = 3)
					
				#setattr(kernel_pdf, 'self.covariance_factor', self.covariance_factor.__get__(kernel_pdf, type(kernel_pdf)))
				#kernel_pdf._compute_covariance()
				cell_kernel_function[i] += [kernel_pdf]
		
		classifier_model_handle.close()

		return cell_kernel_function
	

	def covariance_factor(self, obj):
		return 0.05

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
			likelihood[label] += (self.accel_kernel_function[label][0].evaluate(mean_fv)[0]) * (self.accel_kernel_function[label][1].evaluate(sigma_fv)[0]) *(self.accel_kernel_function[label][2].evaluate(peak_freq_fv)[0]) * (self.accel_kernel_function[label][3].evaluate(strength_var_fv)[0])
		
		posterior_pmf = [0]*5
		for label in xrange(5):
			if sum(likelihood) > 0:
				posterior_pmf[label]=likelihood[label]/(sum(likelihood)*1.0)
			else:
				posterior_pmf[label] = 0.2
				
		return	Distribution(5,posterior_pmf)
	

	def get_ave_intersect_station_ratio(self,window):
		if len(window) < 2:
			return -1
		
		intersect_ratio = 0.0
		for i in xrange(len(window)-1):
			intersect_num = len(list(set(window[i][1]) & set(window[i+1][1])))
			union_num = len(window[i][1]) + len(window[i+1][1]) - intersect_num
			if union_num > 0:
				intersect_ratio += intersect_num/ (union_num*1.0)

		return intersect_ratio/((len(window)-1) * 1.0)

	def rssi_dist_bt_two_scans(self,a,b):
		dist = 0.0
		intersect_num = 0
		bit_map_a = {}
		bit_map_b = {}
		for i in xrange(len(a[1])):
			bit_map_a[i] = 0
		for i in xrange(len(b[1])):
			bit_map_b[i] = 0
	
		for index_list_a in xrange(len(a[1])):
			try:
				index_list_b = b[1].index(a[1][index_list_a])

				intersect_num += 1
				bit_map_a[index_list_a] = 1
				bit_map_b[index_list_b] = 1
				dist += (a[2][index_list_a]  - b[2][index_list_b]) * (a[2][index_list_a] - b[2][index_list_b]) 
			except ValueError:
				continue
		for index_list_a in xrange(len(a[1])):
			if bit_map_a[index_list_a] == 0:
				dist += a[2][index_list_a] * a[2][index_list_a]
		for index_list_b in xrange(len(b[1])):
			if bit_map_b[index_list_b] == 0:
				dist += b[2][index_list_b] * b[2][index_list_b]
	
		union_num = (len(a[1]) + len(b[1]) - intersect_num)
		if union_num > 0:
			return sqrt(dist)/((len(a[1]) + len(b[1]) - intersect_num) * 1.0)
		else:
			return 99

	def get_ave_rssi_diff(self,window):
		if len(window) < 2:
			return -1
	
		total_rssi_diff = 0.0
		for i in xrange(len(window)-1): # for each pair
			total_rssi_diff += self.rssi_dist_bt_two_scans(window[i],window[i+1])

		return total_rssi_diff/((len(window) -1) *1.0)

	def get_ave_instant_speed(self,window):
		if len(window) < 2:
			return -1

		total_speed = 0.0
		for i in xrange(len(window)-1):
			time_diff = (window[i+1][0] - window[i][0])/1000.0
			total_speed += (window[i][1].compute_geo_distance(window[i+1][1]))/time_diff

		return total_speed/((len(window)-1) * 1.0)
	def get_ave_speed(self,window):
		if len(window) < 2:
			return -1
		total_dist = 0.0
		for i in xrange(len(window)-1):
			total_dist += window[i][1].compute_geo_distance(window[i+1][1])

		time_diff = (window[-1][0] - window[0][0])/1000.0

		return float(total_dist)/time_diff

	def m_estimation_smoothing(self,pmf):
		weight = 3
		smoothed_pmf = [sys.float_info.min] * 5
		for label in xrange(5):
			smoothed_pmf[label] = float((weight * pmf[label] + 0.2))/ (weight + 1)
	
		return smoothed_pmf

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		self.wifi_current_window = filter(lambda x: x[0] >= current_time - self.WIFI_WINDOW_IN_MILLI_SECONDS, self.wifi_current_window)
		self.gsm_current_window = filter(lambda x: x[0] >= current_time - self.GSM_WINDOW_IN_MILLI_SECONDS, self.gsm_current_window)
		self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)

		if(isinstance(sensor_reading, GSM)):
			self.gsm_current_window += [(current_time, sensor_reading.cell_tower_list, sensor_reading.rssi_list)]

		if(isinstance(sensor_reading, WiFi)):
			self.wifi_current_window += [(current_time, sensor_reading.ap_list, sensor_reading.rssi_list)]

		if(isinstance(sensor_reading,Accel)):
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
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
		        	self.feature_based_conf_matrix[sensor_reading.gnd_truth][posterior_dist.mode()] += 1
				self.current_accel_fv+=[(current_time,mean,sigma,peak_freq,sigma_valley+sigma_summit)]
					
				# Arbitrary values for unit test :
				self.accel_energy_adapt(current_time, self.power_accel, self.callback_list, posterior_dist.pmf)
				self.last_accel_energy_update=current_time
		
		''' start making prediction '''
		bin_size = 60 * 1000
		cur_bin = current_time/bin_size	
	        self.prev_bin = cur_bin if self.prev_bin == -1 else self.prev_bin	 
		if cur_bin > self.prev_bin: # time to make a prediction
			
			self.prev_bin = cur_bin

			''' get prediction from speed-based sensor'''
			speed_likelihood = [sys.float_info.min] * 5
			speed_posterior = [0.2] * 5
			## wifi
			if self.current_wifi_sampling_interval < max(self.power_wifi.keys()):
				cell_ratio_fv = self.get_ave_intersect_station_ratio(self.wifi_current_window)
				rssi_diff_fv = self.get_ave_rssi_diff(self.wifi_current_window)
				for i in xrange(5):
					speed_likelihood[i] += (self.wifi_kernel_function[i][0].evaluate(cell_ratio_fv)[0]) * (self.wifi_kernel_function[i][1].evaluate(rssi_diff_fv)[0])
				for label in xrange(5):
					if sum(speed_likelihood) > 0:
						speed_posterior[label] = float(speed_likelihood[label])/sum(speed_likelihood)
					else:
						speed_posterior[label] = 0.2

			## gsm
			if self.current_gsm_sampling_interval < max(self.power_gsm.keys()):
				cell_ratio_fv = self.get_ave_intersect_station_ratio(self.gsm_current_window)
				rssi_diff_fv = self.get_ave_rssi_diff(self.gsm_current_window)
				for i in xrange(5):
					speed_likelihood[i] += (self.gsm_kernel_function[i][0].evaluate(cell_ratio_fv)[0]) * (self.gsm_kernel_function[i][1].evaluate(rssi_diff_fv)[0])
				for label in xrange(5):
					if sum(speed_likelihood) > 0:
						speed_posterior[label] = float(speed_likelihood[label])/sum(speed_likelihood)
					else:
						speed_posterior[label] = 0.2
			
			smoothed_speed_posterior = self.m_estimation_smoothing(speed_posterior)
			''' Energy adpative for speed-based sensor'''
			self.speed_energy_adapt(current_time, self.power_gsm, self.power_wifi,self.power_gps, self.callback_list, speed_posterior)
			self.last_speed_energy_update=current_time
			self.classifier_output_speed.append((current_time, smoothed_speed_posterior.index(max(smoothed_speed_posterior))))
			
			''' get prediction from accel '''
			## accel
			self.current_accel_fv = filter(lambda x: x[0] >= current_time - bin_size, self.current_accel_fv)	
			self.current_accel_prediction = filter(lambda x: x[0] >= current_time - bin_size, self.current_accel_prediction)

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
			
			accel_posterior_avefv=self.predict_label(ave_fv_mean,ave_fv_std,ave_fv_pf,ave_fv_sv).pmf
			smoothed_accel_posterior_avefv = self.m_estimation_smoothing(accel_posterior_avefv)
			self.classifier_output_avefv.append((current_time, smoothed_accel_posterior_avefv.index(max(smoothed_accel_posterior_avefv))))
			''' combinr accel and speed based sensors '''
			combined_likelihood = [0]*5
			for label in xrange(5):
				combined_likelihood[label] = smoothed_accel_posterior_avefv[label] * smoothed_speed_posterior[label]
			normalized_combined_posterior = [0]*5
			if sum(combined_likelihood) > 0:
				for i in xrange(5):
					normalized_combined_posterior[i] = float(combined_likelihood[i])/sum(combined_likelihood)
			else:
				normalized_combined_posterior = [0.2] * 5

			self.classifier_output_combined.append((current_time,normalized_combined_posterior.index(max(normalized_combined_posterior))))

			
			current_prediction = normalized_combined_posterior.index(max(normalized_combined_posterior))
			##EWMA
			ALPHA = 0.4
			Yt = [0] * 5
			Yt[current_prediction] = 1
			for i in xrange(5):
				self.ewma_window[i] = ALPHA * Yt[i] + (1-ALPHA) * self.ewma_window[i]

			self.classifier_output_combined_ewma.append((current_time,self.ewma_window.index(max(self.ewma_window))))

			#HMM
			class_prob = normalized_combined_posterior
			#class_prob[current_prediction] = 1.0
							
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
				
			self.classifier_output_combined_hmm.append((current_time,self.state_score.index(max(self.state_score))))



	def speed_energy_adapt(self, current_time, power_gsm, power_wifi, power_gps, callback_list, posterior_pmf):
			self.energy_consumed += (current_time-self.last_speed_energy_update) * power_wifi[self.current_wifi_sampling_interval] 
			self.energy_consumed += (current_time-self.last_speed_energy_update) * power_gps[self.current_gps_sampling_interval] 
			self.energy_consumed += (current_time-self.last_speed_energy_update) * power_gsm[self.current_gsm_sampling_interval] 

			do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2) and (posterior_pmf[update]<=0.8)), callback_list ,False); 
			if (do_i_ramp_up):
				if self.current_gsm_sampling_interval != max(power_gsm.keys()):
					self.current_gsm_sampling_interval = max(power_gsm.keys())
					self.sim_phone.change_gsm_interval(max(power_gsm.keys()))
					self.current_wifi_sampling_interval = 60 * 1000
					self.sim_phone.change_wifi_interval(60 * 1000)
				return
			else:
				if self.current_wifi_sampling_interval != max(power_wifi.keys()):
					self.current_wifi_sampling_interval = max(power_wifi.keys())
					self.sim_phone.change_wifi_interval(max(power_wifi.keys()))
					self.current_gsm_sampling_interval = 60 * 1000
					self.sim_phone.change_gsm_interval(60 * 1000)
				return


	def accel_energy_adapt(self, current_time, power_accel, callback_list, posterior_pmf):
			''' Vary sampling rate if confidence > 0.2'''
			self.energy_consumed += (current_time-self.last_accel_energy_update) * power_accel[self.current_accel_sampling_interval]

			#print "Current sampling interval is ",self.current_sampling_interval
			
			#ramp up if required
			do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2) and (posterior_pmf[update]<=0.8)), callback_list ,False); 
			#do_i_ramp_up=reduce(lambda acc, update : acc or ((posterior_pmf[update] >= 0.2)), callback_list ,False); 
			if (do_i_ramp_up):
				candidate_interval = filter(lambda x : x < self.current_accel_sampling_interval,power_accel)
				if len(candidate_interval) > 0:
					self.current_sampling_interval = max(candidate_interval)
					self.sim_phone.change_accel_interval(self.current_accel_sampling_interval)
				return
			else:
				candidate_interval = filter(lambda x : x > self.current_accel_sampling_interval,power_accel)
				if len(candidate_interval) > 0:
					self.current_sampling_interval = min(candidate_interval)
					self.sim_phone.change_accel_interval(self.current_accel_sampling_interval)
				return
