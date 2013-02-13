#! /usr/bin/python
# generate classification stats
from interval import *
from distributions import *
import sys
class Stats(object) :
	gnd_truth=[]		# list of time, gnd_truth pairs
	classifier_output=[]	# list of time, classifier output pairs
	sampling_intervals=()# 5 tuple of lists each representing one sensor's rate as a fn of time
	callback_list=[]	

	''' power stats for each phone '''
	power_accel=dict()
	power_wifi=dict()
	power_gps=dict()
	power_gsm=dict()
	#power_nwk_loc=dict()
	def __init__ (self,gnd_truth,classifier_output,sensor_sampling_intervals,power_model,callback_list) :
		self.gnd_truth=gnd_truth
		self.classifier_output=classifier_output
		self.sampling_intervals=sensor_sampling_intervals
		self.callback_list=callback_list
		execfile(power_model)

	def match(self,match_type='hard'):	# compute hard metric between the two lists
		# compute bins for both lists
		gnd_truth_bins=self.discretise_time_series(self.gnd_truth)
		output_bins   =self.discretise_time_series(self.classifier_output)
		total_bins=0
		correct_bins=0
		#confusion_matrix = [[0 for i in xrange(6)] for j in xrange(6)]
		for current_bin in gnd_truth_bins:
			if (current_bin in output_bins):
				
				
				merged_gnd_truth_bins = self.merge_not_interested_state(gnd_truth_bins[current_bin])
				merged_output_bins    = self.merge_not_interested_state(output_bins[current_bin])
				if  (set(merged_output_bins).issubset(set(merged_gnd_truth_bins))) and ( merged_output_bins != [] ) and ( merged_gnd_truth_bins != [] ):
					correct_bins+=1
			total_bins+=1

		#print confusion_matrix
		#for activity in xrange(6):
		#	sum_pred = sum(confusion_matrix[activity])
		#	for pred in xrange(6):
		#		confusion_matrix[activity][pred] = float(confusion_matrix[activity][pred])/sum_pred
		
		return float(correct_bins) / (total_bins)
	
	def merge_not_interested_state(self, state_list):
		useless_state = 5
		merged_state_list = []
		for state in state_list:
			if (state in self.callback_list) and (state not in merged_state_list):
				merged_state_list.append(state)
			elif (state not in self.callback_list) and (useless_state not in merged_state_list):
				merged_state_list.append(useless_state)
		return merged_state_list

	def event_match(self, match_type='event'):#TODO: adapt to different kinds of callbacks
		gnd_truth_event=self.eventize_time_series(self.gnd_truth)
		output_event   =self.eventize_time_series(self.classifier_output)
		detected_event_tp = 0
		missed_event_fn = 0
		total_latency = 0.0
		for i in xrange(len(gnd_truth_event)):
			start_time = gnd_truth_event[i][0]
			event = gnd_truth_event[i][1]

			if i == (len(gnd_truth_event) - 1):
				end_time = sys.maxint
			else:
				end_time = gnd_truth_event[i+1][0]

			
			candidate_match = filter(lambda x: x[0] >= start_time and x[0] < end_time and x[1] == event, output_event)
			candidate_match.sort(key = lambda x:x[0])
			if candidate_match == None or len(candidate_match) == 0: # you miss the event :(
				missed_event_fn += 1
			else:
				detected_event_tp += 1
				total_latency = candidate_match[0][0] - start_time
				
		fp = len(output_event) - detected_event_tp
		
		result = {'accuracy': float(detected_event_tp)/ len(gnd_truth_event), 'latency': float(total_latency)/detected_event_tp, 'precision': float(detected_event_tp)/(detected_event_tp + fp), 'recall': float(detected_event_tp)/ (detected_event_tp + missed_event_fn)}

		return result


	def latency_stats(self):# compute latency of detection
		''' find transition points in gnd truth by creating an interval list '''
		gnd_truth_list=self.interval_list(self.gnd_truth)
		for gnd_truth_interval in gnd_truth_list : # for each activity
			classifier_filtered=filter(lambda x : (x[0] >= gnd_truth_interval.start) and (x[0] <= gnd_truth_interval.start + 300*1000), self.classifier_output) # search 300000 ms forward
			for i in range(0,len(classifier_filtered)) :
				consecutive_outputs=classifier_filtered[i:i+10] # check if 10 outputs "hold" our value
				is_detected=reduce(lambda acc,update : acc and update[1].mode()==gnd_truth_interval.distribution.mode(),consecutive_outputs,True)
				if (is_detected) :
					latency=classifier_filtered[i][0]-gnd_truth_interval.start
					actual_label=gnd_truth_interval.distribution.mode()
					print>>sys.stderr,"Activity:",actual_label," starts @ ",gnd_truth_interval.start," Latency: ",latency," ms with ",len(consecutive_outputs)," samples"
					break;

	def energy_stats(self): # compute energy cost of detection over the entire trace
		accel_sampling_intervals  =self.sampling_intervals[0]
		wifi_sampling_intervals   =self.sampling_intervals[1]
		gps_sampling_intervals    =self.sampling_intervals[2]
		gsm_sampling_intervals    =self.sampling_intervals[3]
		#nwk_loc_sampling_intervals=self.sampling_intervals[4]
		energy=0
		for i in range(0,len(accel_sampling_intervals)-1) :
			energy+=self.power_accel[accel_sampling_intervals[i][1]]*(accel_sampling_intervals[i+1][0]-accel_sampling_intervals[i][0])
		for i in range(0,len(wifi_sampling_intervals)-1) :
			energy+=self.power_wifi[wifi_sampling_intervals[i][1]]*(wifi_sampling_intervals[i+1][0]-wifi_sampling_intervals[i][0])
		for i in range(0,len(gps_sampling_intervals)-1) :
			energy+=self.power_gps[gps_sampling_intervals[i][1]]*(gps_sampling_intervals[i+1][0]-gps_sampling_intervals[i][0])
		for i in range(0,len(gsm_sampling_intervals)-1) :
			energy+=self.power_gsm[gsm_sampling_intervals[i][1]]*(gsm_sampling_intervals[i+1][0]-gsm_sampling_intervals[i][0])
		#for i in range(0,len(nwk_loc_sampling_intervals)-1) :
		#	energy+=self.power_nwk_loc[nwk_loc_sampling_intervals[i][1]]*(nwk_loc_sampling_intervals[i+1][0]-nwk_loc_sampling_intervals[i][0])
		return energy	

	def eventize_time_series(self, time_series):

		event_series = []
		prev_event = -1
		for pair in time_series:
			time_stamp = pair[0]
			activity_estimate = pair[1]
			
			if activity_estimate != prev_event:
				event_series += [pair]
				prev_event = activity_estimate

			
		event_series.sort(key=lambda x:x[0])
		return event_series

	def discretise_time_series(self,time_series,bin_size=60000) :
		''' Put the classifier output or the gnd truth into bins of bin_size ms each '''
		binned_time_series=dict()
		for pair in time_series :
			time_stamp=pair[0]
			ml_estimate=pair[1]
			#current_distribution=pair[1]
			#current_distribution=pair[1]
			#ml_estimate=current_distribution.mode()
			bin_index=time_stamp/bin_size
			if bin_index not in binned_time_series :
				binned_time_series[bin_index]=[ml_estimate]
			else :
				if ml_estimate not in binned_time_series[bin_index] :
					binned_time_series[bin_index]+=[ml_estimate]
		return binned_time_series
