#! /usr/bin/python
# train based on traces
from location import *
from sensors import *
from math import *
from numpy.fft import *
from phone import *
import numpy
import sys
from normal import *
class Train(object) :

	''' Windowing primitives '''
	accel_last_update = -1
	wifi_last_update = -1
	gsm_last_update = -1
	gps_last_update = -1
	last_update = -1
	MICRO_WINDOW_IN_MILLI_SEC = 5000
	MACRO_WINDOW_IN_MILLI_SEC = 3 * 60 * 1000
	
	accel_current_window=[]
	accel_micro_window=[]
	gps_current_window=[]
	gsm_current_window=[]
	wifi_current_window=[]

	cur_gsm_feature = {}
	cur_wifi_feature = {}
	cur_accel_feature = {}
	cur_gps_feature = {}	

	def __init__(self,sim_phone, accel_arff_file, gps_arff_file, wifi_arff_file, gsm_arff_file) :
		self.sim_phone=sim_phone
		self.accel_arff_file = accel_arff_file
		self.gps_arff_file = gps_arff_file
		self.wifi_arff_file = wifi_arff_file
		self.gsm_arff_file = gsm_arff_file
		self.sim_phone.change_gsm_interval(60 * 1000)
		self.sim_phone.change_wifi_interval(60 * 1000)
		self.sim_phone.change_gps_interval(60 * 1000)
		self.sim_phone.change_accel_interval(0)


	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)


	def get_ave_intersect_station_ratio(self,window):
		if len(window) < 2:
			return -1
		
		intersect_ratio = 0.0
		for i in xrange(len(window)-1):
			intersect_num = len(list(set(window[i][1]) & set(window[i+1][1])))
			union_num = len(window[i][1]) + len(window[i+1][1]) - intersect_num
			if union_num > 0:
				intersect_ratio += float(intersect_num)/ union_num

		return float(intersect_ratio)/(len(window)-1)

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

		return (total_rssi_diff)/(len(window) -1)

	def tanimoto_dist_bt_two_scans(self,a,b):
		a_length = 0.0
		b_length = 0.0
		dot_length = 0.0

		for index_list_a in xrange(len(a[1])):

			a_length += a[2][index_list_a] * a[2][index_list_a]
			try:
				index_list_b = b[1].index(a[1][index_list_a])
				dot_length += a[2][index_list_a] * b[2][index_list_b]


			except ValueError:
				continue

		for index_list_b in xrange(len(b[1])):
			b_length += b[2][index_list_b] * b[2][index_list_b]
				
		if dot_length == 0:
			return 0
		else:
			return float(dot_length)/(a_length+b_length-dot_length)

	def get_ave_tanimoto_dist(self, window):
		if len(window) < 2:
			return -1
		
		total_tanimoto_dist = 0
		for i in xrange(len(window)-1):
			total_tanimoto_dist += self.tanimoto_dist_bt_two_scans(window[i],window[i+1])

		return float(total_tanimoto_dist)/(len(window)-1)
		
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

	def callback(self,sensor_reading,current_time,gnd_truth):

		
		if(isinstance(sensor_reading, GSM)):
			self.gsm_current_window=filter(lambda x: x[0] >= current_time - self.MACRO_WINDOW_IN_MILLI_SEC, self.gsm_current_window)
			self.gsm_current_window+=[(current_time,sensor_reading.cell_tower_list, sensor_reading.rssi_list)]
			#extract gsm features
			## feature 1: averaged common number of cell towers
			self.cur_gsm_feature['common_cell_ratio']= self.get_ave_intersect_station_ratio(self.gsm_current_window)
			## feature 2: averaged rssi difference
			self.cur_gsm_feature['rssi_dist_ratio'] = self.get_ave_rssi_diff(self.gsm_current_window)
			## feature 3: averaged tanimoto
			self.cur_gsm_feature['tanimoto'] = self.get_ave_tanimoto_dist(self.gsm_current_window)



		if (isinstance(sensor_reading, WiFi)):
			self.wifi_current_window = filter(lambda x: x[0] >= current_time- self.MACRO_WINDOW_IN_MILLI_SEC, self.wifi_current_window)
			self.wifi_current_window += [(current_time,sensor_reading.ap_list,sensor_reading.rssi_list)]
			# extract wifi features
			## feature 1: averaged common number of aps
			self.cur_wifi_feature['common_ap_ratio'] = self.get_ave_intersect_station_ratio(self.wifi_current_window)
			## feature 2: averaged rssi difference
			self.cur_wifi_feature['rssi_dist_ratio'] = self.get_ave_rssi_diff(self.wifi_current_window)
			## feature 3: averaged tanimoto dist
			self.cur_wifi_feature['tanimoto'] = self.get_ave_tanimoto_dist(self.wifi_current_window)
		

		if (isinstance(sensor_reading, GPS)):
			self.gps_current_window= filter(lambda x: x[0] >= current_time - self.MACRO_WINDOW_IN_MILLI_SEC, self.gps_current_window)
			loc = Location(sensor_reading.lat, sensor_reading.lon)
			self.gps_current_window += [(current_time, loc)]
			## feature 1: ave_inst_speed
			self.cur_gps_feature['ave_inst_speed'] = self.get_ave_instant_speed(self.gps_current_window) 
			## feature 2: ave_speed
			self.cur_gps_feature['ave_speed'] =self.get_ave_speed(self.gps_current_window)
		
		if (isinstance(sensor_reading,Accel)) :
			#print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.accel_current_window=filter(lambda x : x[0] >=  current_time - self.MICRO_WINDOW_IN_MILLI_SEC,self.accel_current_window)
		        self.accel_current_window+=[(current_time,accel_mag)]

			self.accel_last_update = current_time if self.accel_last_update == -1 else self.accel_last_update
			if (current_time - self.accel_last_update) >= self.MICRO_WINDOW_IN_MILLI_SEC:
				self.accel_last_update = current_time
				''' variance and mean feature vector components '''
				(mean,variance)=self.mean_and_var(map(lambda x : x[1],self.accel_current_window));
				sigma=sqrt(variance)


				'''Strength Variation'''
				summits=[]
				valleys=[]
				sigma_summit=0
				sigma_valley=0
				for i in xrange(1,len(self.accel_current_window)-1):
					if ( (self.accel_current_window[i][1] >= self.accel_current_window[i+1][1]) and (self.accel_current_window[i][1] >= self.accel_current_window[i-1][1])):
						summits += [self.accel_current_window[i]]
	
					if ( (self.accel_current_window[i][1] <= self.accel_current_window[i+1][1]) and (self.accel_current_window[i][1] <= self.accel_current_window[i-1][1])):
						valleys += [self.accel_current_window[i]]

				if ( len(summits) != 0):
					if self.mean_and_var(map(lambda x: x[1], summits))[1] > 0:
						sigma_summit = sqrt(self.mean_and_var(map(lambda x: x[1],summits))[1])
				if ( len(valleys) != 0):
					if self.mean_and_var(map(lambda x: x[1], valleys))[1] > 0:
						sigma_valley = sqrt(self.mean_and_var(map(lambda x: x[1],valleys))[1])
				
				''' 1Hz - 3Hz coefficient '''
				current_dft =rfft(map(lambda x: x[1], self.accel_current_window))
				if (len(current_dft) > 1):
					peak_freq_index = numpy.abs(current_dft[1:]).argmax() + 1
					dft_coeff = numpy.abs(current_dft)

					N=float(len(self.accel_current_window))
					sampling_freq=N/((self.accel_current_window[-1][0]-self.accel_current_window[0][0])/1000.0)
					peak_freq = ((peak_freq_index)/ (N * 1.0)) * sampling_freq
					nyquist_freq = sampling_freq / 2.0
					assert(peak_freq <= nyquist_freq)
					hz1_mag = -1
					hz2_mag = -2
					hz3_mag = -3
					if (len(current_dft) > int(ceil((3/(sampling_freq*1.0)) * N))):
						hz1_mag = dft_coeff[int(ceil((1/(sampling_freq * 1.0)) * N))]
						hz2_mag = dft_coeff[int(ceil((2/(sampling_freq * 1.0)) * N))]
						hz3_mag = dft_coeff[int(ceil((3/(sampling_freq * 1.0)) * N))]
					#	self.accel_micro_window += [(current_time,mean,sigma,variance,sigma_summit+sigma_valley,peak_freq,hz1_mag,hz2_mag,hz3_mag)]
						accel_feature_str = str(mean) + "," + str(sigma) + "," + str(variance) + "," + str(sigma_summit + sigma_valley) + "," + str(peak_freq) + "," + str(hz1_mag) + "," + str(hz2_mag) + "," + str(hz3_mag) + "," + str(gnd_truth) + "\n"
						self.accel_arff_file.write(accel_feature_str)			
			
			if (current_time - self.gps_last_update) >= self.MACRO_WINDOW_IN_MILLI_SEC and len(self.cur_gps_feature) == 2:
				if self.cur_gps_feature['ave_speed'] == -1:
					return
				self.gps_last_update = current_time
				feature_str = str(self.cur_gps_feature['ave_inst_speed']) + ',' + str(self.cur_gps_feature['ave_speed']) + ',' + str(gnd_truth) + '\n'
				self.gps_arff_file.write(feature_str)

			if (current_time - self.wifi_last_update) >= self.MACRO_WINDOW_IN_MILLI_SEC and len(self.cur_wifi_feature) == 3:
				if self.cur_wifi_feature['common_ap_ratio'] == -1:
					return
				self.wifi_last_update = current_time
				feature_str = str(self.cur_wifi_feature['common_ap_ratio']) + ',' + str(self.cur_wifi_feature['rssi_dist_ratio']) + ',' + str(self.cur_wifi_feature['tanimoto']) + ',' + str(gnd_truth) + '\n'
				self.wifi_arff_file.write(feature_str)
			if (current_time - self.gsm_last_update)  >= self.MACRO_WINDOW_IN_MILLI_SEC and len(self.cur_gsm_feature) ==3:
				if self.cur_gsm_feature['common_cell_ratio'] == -1:
					return
				self.gsm_last_update = current_time
				feature_str = str(self.cur_gsm_feature['common_cell_ratio']) + ',' + str(self.cur_gsm_feature['rssi_dist_ratio']) + ',' + str(self.cur_gsm_feature['tanimoto']) + ',' + str(gnd_truth) + '\n'
				self.gsm_arff_file.write(feature_str)
				
