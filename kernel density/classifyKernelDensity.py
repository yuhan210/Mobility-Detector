#! /usr/bin/python
from sensors import *
from math import *
from numpy.fft import *
import numpy
from normal import *
from distributions import *
import sys
import operator
import pickle
from scipy.stats.kde import gaussian_kde
from scipy.stats import norm

# classify based on traces
class Classify(object) :
	''' Windowing primitives '''
	WINDOW_IN_MILLI_SECONDS=5000
	current_window=[]
	last_print_out = -1

	activity_templates=[]	
	recs = dict()

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	power_nwk_loc=dict()

	feature_list = []
	kernel_function = dict()
	def __init__(self,sim_phone,classifier_model,power_model) :
		self.sim_phone=sim_phone
		self.classifier_output=[]
		
		''' set initial sampling intervals in milliseconds '''
		execfile(power_model)
		self.current_sampling_interval=max(self.power_accel.keys())
		sim_phone.change_accel_interval(max(self.power_accel.keys()))
		sim_phone.change_wifi_interval(max(self.power_wifi.keys()))
		sim_phone.change_gps_interval(max(self.power_gps.keys()))
		sim_phone.change_gsm_interval(max(self.power_gsm.keys()))
		sim_phone.change_nwk_loc_interval(max(self.power_nwk_loc.keys()))
		
			
		classifier_model_handle=open(classifier_model,"r");
		self.feature_list = pickle.load(classifier_model_handle);
		for i in range(5):
			self.kernel_function[i] = []
			for j in range(len(self.feature_list[i])):
				self.kernel_function[i] += [gaussian_kde(self.feature_list[i][j])]
			

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def predict_label(self,mean_fv,sigma_fv,peak_freq_fv,strength_var_fv) :
		''' Predict the label given the mean, sigma, peak frequency and strength variation components of the feature vector '''
		likelihood=[sys.float_info.min]*5
		for label in range(0,5) :
			likelihood[label] += (self.kernel_function[label][0].evaluate(mean_fv)[0]) * (self.kernel_function[label][1].evaluate(sigma_fv)[0]) *(self.kernel_function[label][2].evaluate(peak_freq_fv)[0]) * (self.kernel_function[label][3].evaluate(strength_var_fv)[0])
		posterior_pmf=[0]*5
		for label in range(0,5) :
			posterior_pmf[label]=likelihood[label]/sum(likelihood)
		return	Distribution(5,posterior_pmf)
		

	def shifted_dist_func(self, cur_window, template, detection_step):
		
		time_interval = cur_window[-1][0] - cur_window[0][0]
			
		dists = []
		for i in range(0,len(template),detection_step): # sweep through template
			for j in range(i+1,len(template)):    # find right end point of current candidate
				if template[j][0] - template[i][0] >= time_interval:
					dists.append(self.dist_func(cur_window, template[i:j]))
					break
		# return best match
		return sys.maxint if dists == [] else min(dists)

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
		return sqrt(numpy.sum((downsampled_signal-cur_window_signal)**2))

	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		if (isinstance(sensor_reading,Accel)) :
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.current_window=filter(lambda x : x[0] >=  current_time - self.WINDOW_IN_MILLI_SECONDS,self.current_window)
		        self.current_window+=[(current_time,accel_mag)]
			start_time = self.current_window[0][0]

			self.last_print_out=current_time if self.last_print_out == -1 else self.last_print_out
			if (current_time - self.last_print_out) >= self.WINDOW_IN_MILLI_SECONDS/2.0 :
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
					sigma_summit=sqrt(self.mean_and_var(map(lambda x : x[1],summits))[1]);
				if ( len(valleys) != 0 ) :
					sigma_valley=sqrt(self.mean_and_var(map(lambda x : x[1],valleys))[1]);
				#print "Strength variation ", sigma_valley+sigma_summit
				posterior_dist=self.predict_label(mean,sigma,peak_freq,sigma_valley+sigma_summit)
				print "Posterior", posterior_dist, "gnd_truth", sensor_reading.gnd_truth
				self.classifier_output.append((current_time,posterior_dist))
			
