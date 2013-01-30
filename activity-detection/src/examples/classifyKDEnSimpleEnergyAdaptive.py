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
from location import *
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
	current_sampling_interval = 1000

	feature_list = []
	kernel_function = dict()
	callback_list = []
	#Viterbi
	#stateScore = [0]*5
	prev_prediction = -1
	#EWMA
	ewma_window = []

	use_wifi = 0
	use_gps = 0
	def __init__(self,sim_phone,classifier_model,power_model,callback_list) :
		self.sim_phone=sim_phone
		self.classifier_output=[]
		self.callback_list = callback_list
		self.ewma_window = [0.2]*5

		self.wifi_distribution[0]= Positive_Normal(138.4186,17.2395)
		self.wifi_distribution[1]= Positive_Normal(85.9490,14.2045)
		self.wifi_distribution[2]= Positive_Normal(76.9451,13.8514)
		self.wifi_distribution[3]= Positive_Normal(83.0392, 8.4357)
		self.wifi_distribution[4]= Positive_Normal(32.9173, 32.1233)
		
		self.gps_distribution[0] = Positive_Normal(0.05,0.2)
		self.gps_distribution[1] = Positive_Normal(1.4450, 0.5919)
		self.gps_distribution[2] = Positive_Normal(3.2262, 0.4802)
		self.gps_distribution[3] = Positive_Normal(3.3806, 1.1705)
		self.gps_distribution[4] = Positive_Normal(12.5267, 7.55964)

		for i in range(5):
			print self.wifi_distribution[i]

		hard_act_counter = 0
		for callback in self.callback_list:
			if callback == 0 or callback == 3 or callback == 4:
				hard_act_counter += 1

	#	if hard_act_counter == 1:
	#		self.use_wifi = 1
	#	if hard_act_counter >= 1:
		self.use_gps = 1

		''' set initial sampling intervals in milliseconds '''
		execfile(power_model)
		
		self.current_sampling_interval=max(self.power_accel.keys())
		sim_phone.change_accel_interval(max(self.power_accel.keys()))
		if self.use_wifi == 1:
			sim_phone.change_wifi_interval(60000)
		else:
			sim_phone.change_wifi_interval(10000000000)
		if self.use_gps == 1:
			sim_phone.change_gps_interval(60000)
		else:
			sim_phone.change_gps_interval(10000000000)

		sim_phone.change_gsm_interval(max(self.power_gsm.keys()))
		sim_phone.change_nwk_loc_interval(max(self.power_nwk_loc.keys()))
		
		classifier_model_handle=open(classifier_model,"r");
		self.feature_list = pickle.load(classifier_model_handle);


		for i in range(5):
			self.kernel_function[i] = []
			for j in range(len(self.feature_list[i])):
				kernel_pdf = gaussian_kde(self.feature_list[i][j])
				#kernel_pdf.covariance_factor = lambda : 0.
				#kernel_pdf._compute_covariance()
				self.kernel_function[i] += [kernel_pdf]
		self.feature_list = []

	def compute_geo_distance(self, loc1, loc2):
	# the WGS84 ellipsoid	
		a = 6378137.0#semiMajorAxis
		f = 1.0/298.257223563
		b = (1.0 - f) * a

		phi1 = loc1.latitude * (pi / 180.0)
		lambda1 = loc1.longitude * (pi/ 180.0)
		phi2 = loc2.latitude * (pi/ 180.0)
		lambda2 = loc2.longitude * (pi/ 180.0)

		a2 = a * a
		b2 = b * b
		a2b2b2 = (a2 - b2) / b2

		omega = lambda2 - lambda1

		tanphi1 = tan(phi1)
		tanU1 = (1.0 - f) * tanphi1
		U1 = atan(tanU1)
		sinU1 = sin(U1)
		cosU1 = cos(U1)

		tanphi2 = tan(phi2)
		tanU2 = (1.0 - f) * tanphi2
		U2 = atan(tanU2)
		sinU2 = sin(U2)
		cosU2 = cos(U2)

		sinU1sinU2 = sinU1 * sinU2
		cosU1sinU2 = cosU1 * sinU2
		sinU1cosU2 = sinU1 * cosU2
		cosU1cosU2 = cosU1 * cosU2

		lambda_v = omega

		A = 0.0
		B = 0.0
		sigma = 0.0
		deltasigma = 0.0
		lambda0 = lambda_v
		converged = 0
		for i in range(20):
			lambda0 = lambda_v
			sinlambda = sin(lambda_v)
			coslambda = cos(lambda_v)

			sin2sigma = ( cosU2 * sinlambda * cosU2 * sinlambda ) + (cosU1sinU2 - sinU1cosU2 * coslambda) * (cosU1sinU2 - sinU1cosU2 * coslambda)
			sinsigma = sqrt(sin2sigma)

			cossigma = sinU1sinU2 + (cosU1cosU2 * coslambda)

			sigma = atan2(sinsigma, cossigma)
			
			if (sin2sigma == 0):
				sinalpha = 0.0
			else:
				sinalpha = cosU1cosU2 * sinlambda / sinsigma

			alpha = asin(sinalpha)
			cosalpha = cos(alpha)
			cos2alpha = cosalpha * cosalpha

			if (cos2alpha == 0):
				cos2sigmam = 0
			else:
				cos2sigmam = cossigma -2 * sinU1sinU2/cos2alpha
			
			u2 = cos2alpha * a2b2b2

			cos2sigmam2 = cos2sigmam * cos2sigmam

			A = 1.0 + u2 / 16384 * (4096 + u2 * ( -768 + u2 * (320 - 175 * u2)))

			B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74-47 * u2)))

			deltasigma = B * sinsigma * (cos2sigmam + B /4 * (cossigma * ( -1 +2 * cos2sigmam2) -B /6 * cos2sigmam * (-3 +4 * sin2sigma) * (-3 +4 *cos2sigmam2)))
			C = f/ 16 * cos2alpha * (4 + f * (4-3*cos2alpha))

			lambda_v = omega + (1- C) *f * sinalpha * (sigma + C *sinsigma * (cos2sigmam + C * cossigma * (-1+2* cos2sigmam2)))


			if lambda_v == 0: 
				change = 0.1
			else:
				change = abs((lambda_v-lambda0)/lambda_v)

			if (i > 1) and change < 0.0000000000001:
				converged = 1
				break
			s = b * A * (sigma - deltasigma)
			print "distance", s 

			return s

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
			if sum(likelihood) > 0:
				posterior_pmf[label]=likelihood[label]/sum(likelihood)
			else:
				posterior_pmf[label] = 0.2
		return	Distribution(5,posterior_pmf)

	def gps_predict_label(self, set_of_gps_points):
		if len(set_of_gps_points) < 2:
			return	(Distribution(5,[0.2]*5), 0)
		
		total_distance = 0
		prev_dist = -1
		for coord_index in range(len(set_of_gps_points)-1):
			
			coord_1 = Location(set_of_gps_points[coord_index].lat, set_of_gps_points[coord_index].lon)
			coord_2 = Location(set_of_gps_points[coord_index+1].lat, set_of_gps_points[coord_index+1].lon)
			print "loc1.lat", coord_1.latitude, "loc1.long", coord_1.longitude
			print "loc2.lat", coord_2.latitude, "loc2.long", coord_2.longitude

			distance =  self.compute_geo_distance(coord_1,coord_2)	
			
			total_distance += distance

		ave_speed = total_distance /((set_of_gps_points[-1].time_stamp -set_of_gps_points[0].time_stamp)/1000.0)
		
		print "GPS ave speed", ave_speed, "total distance", total_distance
			
		if total_distance > 4500 * 2 : # this guy is crazy

			return (Distribution(5,[0.2]*5), 0)
		else:
			self.gps_distribution
			likelihood = [sys.float_info.min] * 5
			for label in range(0,5):
				likelihood[label] += (self.gps_distribution[label].pdf(ave_speed))
		
			posterior_pmf=[0]*5
			for label in range(0,5) :
				if sum(likelihood) > 0:
					posterior_pmf[label]=likelihood[label]/sum(likelihood)
				else:
					posterior_pmf[label] = 0.2
			
			return	(Distribution(5,posterior_pmf),1)
			

	def wifi_predict_label(self, set_of_wifi_obs, wifi_distribution):
	
		if len(set_of_wifi_obs) < 2:
			return	(Distribution(5,[0.2]*5), 0)
		

		matrix_list = []
		for i in range(len(set_of_wifi_obs)-1):
			cur_wifi_ob = set_of_wifi_obs[i]
			nxt_wifi_ob= set_of_wifi_obs[i+1]
			
			cur_wifi_bit = [0]*len(cur_wifi_ob.ap_list)
			nxt_wifi_bit = [0]*len(nxt_wifi_ob.ap_list)
			
			pair_dist = 0
			intersect_num = 0
			for j in range(len(cur_wifi_ob.ap_list)):
				for k in range(len(nxt_wifi_ob.ap_list)):
					if cur_wifi_ob.ap_list[j].find(nxt_wifi_ob.ap_list[k]) >= 0:
						cur_wifi_bit[j] = 1
						nxt_wifi_bit[k] = 1
						pair_dist += (cur_wifi_ob.rssi_list[j] - nxt_wifi_ob.rssi_list[k])* (cur_wifi_ob.rssi_list[j] - nxt_wifi_ob.rssi_list[k])
						intersect_num += 1
						break

			for j in range(len(cur_wifi_ob.ap_list)):
				if (cur_wifi_bit[j] == 0):
					pair_dist += (cur_wifi_ob.rssi_list[j] * cur_wifi_ob.rssi_list[j])

			for k in range(len(nxt_wifi_ob.ap_list)):
				if (nxt_wifi_bit[k] == 0):
					pair_dist += (nxt_wifi_ob.rssi_list[k] * nxt_wifi_ob.rssi_list[k])

			pair_dist = sqrt(pair_dist)
			union_num = len(cur_wifi_ob.ap_list) + len(nxt_wifi_ob.ap_list) - intersect_num
			matrix = 0
			if union_num > 0:
				matrix = 99 * (intersect_num/(union_num*1.0)) + ( 99 - (pair_dist/(union_num *1.0)))

			matrix_list.append(matrix)	
			
		(mean,var)=self.mean_and_var(matrix_list)
		
		print "Wifi-matrix", mean
		likelihood = [sys.float_info.min] * 5
		for label in range(0,5):
			likelihood[label] += (self.wifi_distribution[label].pdf(mean))
		
		posterior_pmf=[0]*5
		for label in range(0,5) :
			if sum(likelihood) > 0:
				posterior_pmf[label]=likelihood[label]/sum(likelihood)
			else:
				posterior_pmf[label] = 0.2
		

		return	(Distribution(5,posterior_pmf),1)



	def callback(self,sensor_reading,current_time) :
		''' Interface to simulator :  Leave final result as (timestamp,output_distribution) pairs in classifier_output '''
		

		bin_size = 60 * 1000
		cur_bin = current_time/bin_size
			
	        self.prev_bin = cur_bin if self.prev_bin == -1 else self.prev_bin	 

		if cur_bin > self.prev_bin: # time to make a prediction
			
			self.prev_bin = cur_bin
			
			##GPS
			self.current_gps_obs= filter(lambda x: x.time_stamp >= current_time - self.GPS_WINDOW_IN_MILLI_SECONDS, self.current_gps_obs)
			
			(gps_posterior_dist, should_i_trust_gps) = self.gps_predict_label(self.current_gps_obs)
			#if (should_i_trust_gps == -1):
			#	gps_posterior_dist = final_posterior_dist

			print "gps_dist" , gps_posterior_dist
			## wifi			
			self.current_wifi_obs= filter(lambda x: x.time_stamp >= current_time - self.WIFI_WINDOW_IN_MILLI_SECONDS ,self.current_wifi_obs)
			(wifi_posterior_dist,should_i_trust_wifi) = self.wifi_predict_label(self.current_wifi_obs, self.wifi_distribution)
			
			print "wifi-dist", wifi_posterior_dist
				

			## accel
			self.current_accel_fv = filter(lambda x: x[0] >= current_time -  bin_size, self.current_accel_fv)	
			self.current_accel_prediction = filter(lambda x: x[0] >= current_time - bin_size, self.current_accel_prediction)
 
			## new scheme
			prediction_list = [0]*5
			for prediction_tuple in self.current_accel_prediction:
				prediction_list[prediction_tuple[1]] += 1				
		
			accel_likelihood= [0] *5
			for i in range(5):
				accel_likelihood[i] = prediction_list[i]/(sum(prediction_list)*1.0) 
			print "accel_likelihood", accel_likelihood
			##

		   	accel_mean_list = []
			accel_std_list = []
			accel_pf_list = []
			accel_sv_list = []
			for accel_tuple in self.current_accel_fv:
				for i in range(1,len(accel_tuple)):
					if i == 1:
						accel_mean_list.append(accel_tuple[i])
					elif i == 2:
						accel_std_list.append(accel_tuple[i])
					elif i == 3:
						accel_pf_list.append(accel_tuple[i])
					elif i == 4:
						accel_sv_list.append(accel_tuple[i])
			(ave_fv_mean,dumb) = self.mean_and_var(accel_mean_list)
			(ave_fv_std,dumb) = self.mean_and_var(accel_std_list)
			(ave_fv_pf,dumb) = self.mean_and_var(accel_pf_list)
			(ave_fv_sv,dumb) = self.mean_and_var(accel_sv_list)
			
			accel_posterior_dist=self.predict_label(ave_fv_mean,ave_fv_std,ave_fv_pf,ave_fv_sv)
			
			if (self.use_wifi == 1):
					
				if max(wifi_posterior_dist.pmf) > 0.8:
				#if should_i_trust_wifi == 1 and (wifi_posterior_dist.mode() == 0 or wifi_posterior_dist.mode() == 4):
					final_posterior_pmf = wifi_posterior_dist.pmf	
					print "Prediction from wifi(sole)", wifi_posterior_dist
			
				else:
					combined_posterior_pmf = [0]*5
					
					for i in range(5):
				#		combined_posterior_pmf[i] = accel_posterior_dist.pmf[i] * wifi_posterior_dist.pmf[i]
						combined_posterior_pmf[i] = accel_likelihood[i] * wifi_posterior_dist.pmf[i]
				
					for label in range(5) :
						if sum(combined_posterior_pmf) > 0:
							combined_posterior_pmf[label]=combined_posterior_pmf[label]/sum(combined_posterior_pmf)

					print "wifi+accel combined", combined_posterior_pmf
					final_posterior_pmf = combined_posterior_pmf	
			
			if (self.use_gps == 1):
				if should_i_trust_gps == 1: 
					if (gps_posterior_dist.mode() == 0 or gps_posterior_dist.mode() == 4): 	
				#if max(gps_posterior_dist.pmf) > 0.8: 	
						final_posterior_pmf = gps_posterior_dist.pmf	
						print "Prediction from gps(sole)", gps_posterior_dist
					else:	
						combined_posterior_pmf = [0]*5
						for i in range(1,4):
							#combined_posterior_pmf[i] = accel_posterior_dist.pmf[i] * gps_posterior_dist.pmf[i]
							combined_posterior_pmf[i] = accel_posterior_dist.pmf[i] * gps_posterior_dist.pmf[i]
				
						for label in range(5) :
							if sum(combined_posterior_pmf) > 0:
								combined_posterior_pmf[label]=combined_posterior_pmf[label]/sum(combined_posterior_pmf)

						print "Prediction from accel(ref)", accel_posterior_dist
						print "gps+accel combined", combined_posterior_pmf
						#final_posterior_pmf = gps_posterior_dist.pmf	
						final_posterior_pmf = combined_posterior_pmf	
				else:
					final_posterior_pmf = accel_posterior_dist.pmf

			

			if (self.use_gps == 0 and self.use_wifi == 0):
					
					#final_posterior_pmf = accel_posterior_dist.pmf	
					final_posterior_pmf = accel_likelihood
					print "Prediction from accel(sole", accel_posterior_dist
					
					

		
			final_posterior_dist = Distribution(5,final_posterior_pmf)
			print "++++gnd_truth++++", sensor_reading.gnd_truth
			print "++++Final posterior dist++++", final_posterior_dist
			#self.classifier_output.append((current_time,final_posterior_dist))
			## EWMA
			current_prediction = final_posterior_dist.mode()
			ALPHA = 0.2
			Yt = [0]*5
			Yt[current_prediction] = 1
			for i in range(5):
				self.ewma_window[i] = ALPHA * Yt[i] + (1-ALPHA) * self.ewma_window[i]
					
			print "ewma", self.ewma_window
			maxIndex = self.ewma_window.index(max(self.ewma_window))
			pmf = [0]*5
			pmf[maxIndex] = 1
			print "smoothed", Distribution(5,pmf)
			self.classifier_output.append((current_time,Distribution(5, pmf)))

		if (isinstance(sensor_reading,GPS) and self.use_gps == 1):
			self.current_gps_obs +=[sensor_reading]

		if (isinstance(sensor_reading,WiFi) and self.use_wifi == 1):

			if len(sensor_reading.ap_list) > 0:
				self.current_wifi_obs+=[sensor_reading]	
		

		#	self.current_accel_fv=filter(lambda x : x[0] >=  current_time - 60 * 1000,self.current_accel_fv)
			
		#   	accel_mean_list = []
		#	accel_std_list = []
		#	accel_pf_list = []
		#	accel_sv_list = []
		#	for accel_tuple in self.current_accel_fv:
		#		for i in range(1,len(accel_tuple)):
		#			if i == 1:
		#				accel_mean_list.append(accel_tuple[i])
		#			elif i == 2:
		#				accel_std_list.append(accel_tuple[i])
		#			elif i == 3:
		#				accel_pf_list.append(accel_tuple[i])
		#			elif i == 4:
		#				accel_sv_list.append(accel_tuple[i])
		#	ave_fv_mean = self.mean_and_var(accel_mean_list)
		#	ave_fv_std = self.mean_and_var(accel_std_list)
		#	ave_fv_pf = self.mean_and_var(accel_pf_list)
		#	ave_fv_sv = self.mean_and_var(accel_sv_list)
		#	posterior_dist=self.predict_label(ave_fv_mean,ave_fv_std,ave_fv_pf,ave_fv_sv)

	

		#	self.current_wifi_obs= filter(lambda x: x.time_stamp >= current_time - self.WIFI_WINDOW_IN_MILLI_SECONDS ,self.current_wifi_obs)
		#	print self.current_wifi_obs	
		#	if len(sensor_reading.ap_list) > 0:
		#		self.current_wifi_obs+=[sensor_reading]	
			
		#	if len(self.current_wifi_obs) > 1: ## a window of wifi fingerprints
		#		print "current_time", current_time , self.current_wifi_obs
					
		#		wifi_posterior_dist = self.get_wifi_fingerprint_dist(self.current_wifi_obs, self.wifi_distribution)
		#		print "wifi-dist", wifi_posterior_dist
				#self.classifier_output.append((current_time,Distribution(5, pmf)))
				
				#averaged_ap_num = sum(map(lambda x : len(x.ap_list), self.current_wifi_obs))/len(self.current_wifi_obs)
				#averaged_max_rssi = sum(map(lambda x : max(x.rssi_list),self.current_wifi_obs))/len(self.current_wifi_obs)
				
				#print "averaged_ap_num", averaged_ap_num, "averaged_max_rssi", averaged_max_rssi
				#if averaged_ap_num >= 10 and averaged_max_rssi > -80:
				#	self.might_be_driving = 0	
				#else:
				#	self.might_be_driving = 1
				#if wifi_matrix_mean > 120:
				#	self.must_be_static = 0
				#else:
				#	self.must_be_static = 0

				#if wifi_matrix_mean < 70 and len(self.current_wifi_obs) > 0:
				#	self.must_be_driving = 0
				#else:
				#	self.must_be_driving = 0
		#		combined_posterior_pmf = [0]*5
		#		for i in range(5):
		#			combined_posterior_pmf[i] = posterior_dist.pmf[i] * wifi_posterior_dist.pmf[i]
				
		#		for label in range(0,5) :
		#			if sum(combined_posterior_pmf) > 0:
		#				combined_posterior_pmf[label]=combined_posterior_pmf[label]/sum(combined_posterior_pmf)

		#		print "combined", combined_posterior_pmf
		#		self.classifier_output.append((current_time,Distribution(5, combined_posterior_pmf)))
		#	else:	
			
		#		self.classifier_output.append((current_time,posterior_dist))
		#		print "combined", posterior_dist


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
				
				#posterior_dist=self.predict_label_with_wifi_hint(mean,sigma,peak_freq,sigma_valley+sigma_summit, self.must_be_driving, self.must_be_static)
				#print "gnd_truth", sensor_reading.gnd_truth
				print "Posterior", posterior_dist
				#self.classifier_output.append((current_time,posterior_dist))
				# Arbitrary values for unit test :
				self.simple_energy_adapt(current_time, self.power_accel, self.callback_list, posterior_dist.pmf)
				self.last_energy_update=current_time
					
				#self.classifier_output.append((current_time,posterior_dist))

				## EWMA
				#current_prediction = posterior_dist.mode()
				#ALPHA = 0.20
				#Yt = [0]*5
				#Yt[current_prediction] = 1
				#for i in range(5):
				#	self.ewma_window[i] = ALPHA * Yt[i] + (1-ALPHA) * self.ewma_window[i]
					
				#print "ewma", self.ewma_window
				#maxIndex = self.ewma_window.index(max(self.ewma_window))
				#pmf = [0]*5
				#pmf[maxIndex] = 1
				#self.classifier_output.append((current_time,Distribution(5, pmf)))

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
