#! /usr/bin/python
# train based on traces
from location import *
from sensors import *
from math import *
from numpy.fft import *
import numpy
import sys
class Train(object) :

	''' Windowing primitives '''
	accel_last_print_out=-1
	last_print_out = -1
	WINDOW_IN_MILLI_SECONDS=1000
	PRED_WINDOW_IN_MILLI_SEC=60 * 1000
	MICRO_WINDOW_IN_MILLI_SEC = 5000
	MACRO_WINDOW_IN_MILLI_SEC = 60 * 1000
	
	accel_current_window=[]
	accel_micro_window=[]
	gps_current_window=[]
	gsm_current_window=[]
	wifi_current_window=[]

	cur_gsm_feature = {}
	cur_wifi_feature = {}
	cur_accel_feature = {}
	cur_gps_feature = {}	
	def __init__(self,sim_phone, arff_file) :
		self.sim_phone=sim_phone
		self.arff_file = arff_file
	
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

	def check_keys(self):
	#	if self.cur_accel_feature.has_key('var') == True and self.cur_accel_feature.has_key('1hz') == True and self.cur_accel_feature.has_key('2hz') == True and self.cur_accel_feature.has_key('3hz') == True and self.cur_gsm_feature.has_key('common_cell_ratio') == True and self.cur_gsm_feature.has_key('rssi_dist_ratio') == True and self.cur_wifi_feature.has_key('common_ap_ratio') == True and self.cur_wifi_feature.has_key('rssi_dist_ratio') == True and self.cur_gps_feature.has_key('speed') == True:
		if self.cur_accel_feature.has_key('var') == True and self.cur_accel_feature.has_key('1hz') == True and self.cur_accel_feature.has_key('2hz') == True and self.cur_accel_feature.has_key('3hz') == True and self.cur_wifi_feature.has_key('common_ap_ratio') == True and self.cur_wifi_feature.has_key('rssi_dist_ratio') == True and self.cur_gps_feature.has_key('speed') == True:
			return 1
		else:
			return 0
	def get_ave_speed(self,window):
		if len(window) < 2:
			return -1

		total_speed = 0.0
		for i in xrange(len(window)-1):
			time_diff = (window[i+1][0] - window[i][0])/1000.0
			total_speed += (window[i][1].compute_geo_distance(window[i+1][1]))/time_diff

		return total_speed/((len(window)-1) * 1.0)

	def callback(self,sensor_reading,current_time,gnd_truth):

		
		if (isinstance(sensor_reading, GSM)):
			print sensor_reading
			self.gsm_current_window=filter(lambda x: x[0] >= current_time - self.MACRO_WINDOW_IN_MILLI_SEC, self.gsm_current_window)
			self.gsm_current_window+=[(current_time,sensor_reading.cell_tower_list, sensor_reading.rssi_list)]
			print self.gsm_current_window
			#extract gsm features
			## feature 1: averaged common number of cell towers
			self.cur_gsm_feature['common_cell_ratio']= self.get_ave_intersect_station_ratio(self.gsm_current_window)
			print self.cur_gsm_feature
			## feature 2: averaged rssi difference
			self.cur_gsm_feature['rssi_dist_ratio'] = self.get_ave_rssi_diff(self.gsm_current_window)

			

		if (isinstance(sensor_reading, WiFi)):
			self.wifi_current_window = filter(lambda x: x[0] >= current_time- self.MACRO_WINDOW_IN_MILLI_SEC, self.wifi_current_window)
			self.wifi_current_window += [(current_time,sensor_reading.ap_list,sensor_reading.rssi_list)]
			# extract wifi features
			## feature 1: averaged common number of aps
			self.cur_wifi_feature['common_ap_ratio'] = self.get_ave_intersect_station_ratio(self.wifi_current_window)
			## feature 2: averaged rssi difference
			self.cur_wifi_feature['rssi_dist_ratio'] = self.get_ave_rssi_diff(self.wifi_current_window)


		if (isinstance(sensor_reading, GPS)):
			self.gps_current_window= filter(lambda x: x[0] >= current_time - self.MACRO_WINDOW_IN_MILLI_SEC, self.gps_current_window)
			loc = Location(sensor_reading.lat, sensor_reading.lon)
			self.gps_current_window += [(current_time, loc)]
			## feature 1: ave_speed
			self.cur_gps_feature['speed'] = self.get_ave_speed(self.gps_current_window) 
		
		if (isinstance(sensor_reading,Accel)) :
			#print "\n"
			''' compute accel magnitude and keep track of windows '''
			accel_mag=sqrt(sensor_reading.accel_x**2+sensor_reading.accel_y**2+sensor_reading.accel_z**2)
		        self.accel_current_window=filter(lambda x : x[0] >=  current_time - self.MICRO_WINDOW_IN_MILLI_SEC,self.accel_current_window)
		        self.accel_current_window+=[(current_time,accel_mag)]

			self.accel_last_print_out = current_time if self.accel_last_print_out == -1 else self.accel_last_print_out
			if (current_time - self.accel_last_print_out) >= self.MICRO_WINDOW_IN_MILLI_SEC:
				self.accel_last_print_out = current_time
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
						self.accel_micro_window += [(current_time,variance,sigma_summit+sigma_valley,peak_freq,hz1_mag,hz2_mag,hz3_mag)]
			
			self.accel_micro_window = filter(lambda x: x[0] >= current_time - self.MACRO_WINDOW_IN_MILLI_SEC, self.accel_micro_window) 	
			if len(self.accel_micro_window) > 0:
				self.cur_accel_feature['var'] = sum(map(lambda x: x[1], self.accel_micro_window))/(len(self.accel_micro_window) * 1.0)
				self.cur_accel_feature['sv'] = sum(map(lambda x: x[2], self.accel_micro_window))/(len(self.accel_micro_window) * 1.0)
				self.cur_accel_feature['pf'] = sum(map(lambda x: x[3], self.accel_micro_window))/(len(self.accel_micro_window) * 1.0)
				self.cur_accel_feature['1hz'] = sum(map(lambda x: x[4], self.accel_micro_window))/(len(self.accel_micro_window) * 1.0)
				self.cur_accel_feature['2hz'] = sum(map(lambda x: x[5], self.accel_micro_window))/(len(self.accel_micro_window) * 1.0)
				self.cur_accel_feature['3hz'] = sum(map(lambda x: x[6], self.accel_micro_window))/(len(self.accel_micro_window) * 1.0)

		self.last_print_out = current_time if self.last_print_out == -1 else self.last_print_out
		if (current_time - self.last_print_out) >= self.MACRO_WINDOW_IN_MILLI_SEC:
			self.last_print_out = current_time
	#		print gnd_truth	
			#print self.cur_accel_feature
	#		print self.cur_gsm_feature
			#print self.cur_wifi_feature
	#		print self.cur_gps_feature
			if self.check_keys() == 1:
		#		feature_str = str(self.cur_accel_feature['var']) + "," + str(self.cur_accel_feature['1hz']) + "," + str(self.cur_accel_feature['2hz']) + "," + str(self.cur_accel_feature['3hz'])+ ","+ str(self.cur_gsm_feature['common_cell_ratio'])+","+ str(self.cur_gsm_feature['rssi_dist_ratio']) + "," + str(self.cur_wifi_feature['common_ap_ratio']) +","+ str(self.cur_wifi_feature['rssi_dist_ratio'])+ ","+  str(self.cur_gps_feature['speed'])+","+ str(gnd_truth) + "\n"
				feature_str = str(self.cur_accel_feature['var']) + "," + str(self.cur_accel_feature['sv']) +","+ str(self.cur_accel_feature['pf'])+"," + str(self.cur_accel_feature['1hz']) + "," + str(self.cur_accel_feature['2hz']) + "," + str(self.cur_accel_feature['3hz'])+ "," + str(self.cur_wifi_feature['common_ap_ratio']) +","+ str(self.cur_wifi_feature['rssi_dist_ratio'])+ ","+  str(self.cur_gps_feature['speed'])+","+ str(gnd_truth) + "\n"
	#			print feature_str
				self.arff_file.write(feature_str)	
			
	def output_classifer(self) :

		self.arff_file.close()
