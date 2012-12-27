#! /usr/bin/python
# class representing phone
from sensors import *
from distributions import *
import sys
class Phone(object) :
	''' sampling interval defaults in milliseconds '''
	accel_interval=1000
	wifi_interval=1000
	gps_interval=1000
	gsm_interval=1000
	nwk_loc_interval=1000
	
	''' current time on trace '''
	current_time=0

	''' gnd truth list '''
	gnd_truth=[]

	''' trace file names '''
	accel_trace=""
	wifi_trace=""
	gps_trace=""
	gsm_trace=""
	nwk_loc_trace=""

	''' sensor reading lists '''	
	accel_list=[]
	wifi_list=[]
	gps_list=[]
	gsm_list=[]
	nwk_loc_list=[]

	''' next sensor timestamp (for downsampling) '''
	next_accel_timestamp=-1
	next_wifi_timestamp=-1
	next_gps_timestamp=-1
	next_gsm_timestamp=-1
	next_nwk_loc_timestamp=-1

	''' sampling rate vectors for sensors '''
	accel_sampling_intervals=[]
	wifi_sampling_intervals=[]
	gps_sampling_intervals=[]
	gsm_sampling_intervals=[]
	nwk_loc_sampling_intervals=[]

	def __init__ (self,accel_trace,wifi_trace,gps_trace,gsm_trace,nwk_loc_trace) :
		''' Populate trace file names '''
		self.accel_trace=accel_trace
		self.wifi_trace=wifi_trace
		self.gps_trace=gps_trace
		self.gsm_trace=gsm_trace
		self.nwk_loc_trace=nwk_loc_trace
		''' Read them into lists '''
		self.event_list=[]
		self.accel_list=[]
		self.gps_list=[]
		self.wifi_list=[]
		self.gsm_list=[]
		self.nwk_loc_list=[]
		self.read_accel_trace()
		#self.read_wifi_trace()
		self.read_gps_trace()
		#self.read_gsm_trace()
		#self.read_nwk_loc_trace()
		''' Sort event list using timestamp as key;TODO: Fix invalid timestamps '''
		self.event_list=self.accel_list+self.wifi_list+self.gps_list+self.gsm_list+self.nwk_loc_list;
		self.event_list.sort(key=lambda x : x.time_stamp) 
		self.current_time=self.event_list[0].time_stamp
		''' Populate next timestamps '''
		self.next_accel_timestamp=self.accel_list[0].time_stamp if self.accel_list != [] else sys.float_info.max
		self.next_wifi_timestamp=self.wifi_list[0].time_stamp if self.wifi_list != [] else sys.float_info.max
		self.next_gps_timestamp=self.gps_list[0].time_stamp if self.gps_list != [] else sys.float_info.max
		self.next_gsm_timestamp=self.gsm_list[0].time_stamp if self.gsm_list != [] else sys.float_info.max
		self.next_nwk_loc_timestamp=self.nwk_loc_list[0].time_stamp if self.nwk_loc_list != [] else sys.float_info.max
	''' Methods to change sampling interval '''
	def change_accel_interval(self,accel_interval):
		if( self.accel_interval == accel_interval ) :
			return
		self.accel_interval=accel_interval
		self.next_accel_timestamp=self.current_time+self.accel_interval
		self.accel_sampling_intervals.append((self.current_time,self.accel_interval));
	def change_wifi_interval(self,wifi_interval):
		if( self.wifi_interval == wifi_interval ) :
			return
		self.wifi_interval=wifi_interval
		self.next_wifi_timestamp=self.current_time+self.wifi_interval
		self.wifi_sampling_intervals.append((self.current_time,self.wifi_interval));		
	def change_gps_interval(self,gps_interval):
		if( self.gps_interval == gps_interval ) :
			return
		self.gps_interval=gps_interval
		self.next_gps_timestamp=self.current_time+self.gps_interval
		self.gps_sampling_intervals.append((self.current_time,self.gps_interval));
	def change_gsm_interval(self,gsm_interval):
		if( self.gsm_interval == gsm_interval ) :
			return
		self.gsm_interval=gsm_interval
		self.next_gsm_timestamp=self.current_time+self.gsm_interval
		self.gsm_sampling_intervals.append((self.current_time,self.gsm_interval));
	def change_nwk_loc_interval(self,nwk_loc_interval) :
		if( self.nwk_loc_interval == nwk_loc_interval ) :
			return
		self.nwk_loc_interval=nwk_loc_interval
		self.next_nwk_loc_timestamp=self.current_time+self.nwk_loc_interval
		self.nwk_loc_sampling_intervals.append((self.current_time,self.nwk_loc_interval));


	''' File handling routines '''
	def read_accel_trace (self) :
		fh=open(self.accel_trace,"r");
		for line in fh.readlines() :
			records=line.split(',')
			try :
				time_stamp=int(float(records[1]))
				gnd_truth=int(records[3].split('|')[3])
				accel_reading=Accel(float(records[3].split('|')[0]),float(records[3].split('|')[1]),float(records[3].split('|')[2]),time_stamp,gnd_truth)
				self.accel_list+=[accel_reading]
			except Exception :
				continue
			
	def read_wifi_trace (self) :
		fh=open(self.wifi_trace,"r");
		for line in fh.readlines() :
			try :
				records=line.split(',')
				time_stamp=int(float(records[1]))
				gnd_truth=int(records[3].split('|')[5])
				wifi_scan_data=records[3]
				''' determine number of APs '''
				num_aps=int(wifi_scan_data.split('|')[4])
				i=0
				ap_name=wifi_scan_data.split('|')[2]
				bss_list=[]
				rssi_list=[]
				if (ap_name != 'null') : # invalid AP
					bss_list =[ap_name]
					rssi_list=[int(wifi_scan_data.split('|')[3])]
				for i in range(0,num_aps) :
					next_ap_data=wifi_scan_data.split('|')[6+4*i:6+4*i+4]
					
					''' Modified '''
					if len(next_ap_data) < 2:
						continue
					''' Modified '''
					ap_name=next_ap_data[1];
					if (ap_name!='null') : # invalid AP
						bss_list+=[ap_name];
						rssi_list+=[int(next_ap_data[2])];
				assert(len(bss_list)==len(rssi_list))	
				self.wifi_list+=[WiFi(bss_list,rssi_list,time_stamp,gnd_truth)]
			except Exception :
				continue
			
	def read_gps_trace (self) :
		fh=open(self.gps_trace,"r");
		for line in fh.readlines() :
			try :
				records=line.split(',')
				time_stamp=int(float(records[1]))
				gnd_truth=int(records[3].split('|')[8])
				gps_reading=GPS(float(records[3].split('|')[2]),float(records[3].split('|')[3]),time_stamp,gnd_truth, float(records[3].split('|')[6]))
				self.gps_list+=[gps_reading]

			except Exception :
				continue
	def read_gsm_trace (self) :
		fh=open(self.gsm_trace,"r");
		for line in fh.readlines() :
			try :
				records=line.split(',')
				time_stamp=int(float(records[1]))
				gnd_truth=int(records[3].split('|')[5])
				gsm_scan_data=records[3]
				''' determine number of Base Stations '''
				num_bs=int(gsm_scan_data.split('|')[6])
				i=0
				rssi=int(gsm_scan_data.split('|')[2])
				bs_list=[]
				rssi_list=[]
				if (rssi != 99) : # invalid RSSI
					bs_list =[gsm_scan_data.split('|')[0]]
					rssi_list=[rssi]
				for i in range(0,num_bs) :
					next_bs_data=gsm_scan_data.split('|')[7+3*i:7+3*i+3]
					''' Modified '''
					if len(next_bs_data) < 3:
						continue
					rssi=int(next_bs_data[2])
					if (rssi != 99) : # invalid RSSI
						bs_list+=[next_bs_data[0]];
						rssi_list+=[rssi];
				assert(len(bs_list)==len(rssi_list))	
				self.gsm_list+=[GSM(bs_list,rssi_list,time_stamp,gnd_truth)]
			except Exception :
				continue
	''' TODO Data format changed before May 2012. Now, the after May 2012 format is implemented '''

	def read_nwk_loc_trace (self) :
		fh=open(self.nwk_loc_trace,"r");
		for line in fh.readlines() :
			try :
				records=line.split(',')
				time_stamp=int(float(records[1]))
				gnd_truth=int(records[3].split('|')[8])
				nwk_loc_reading=NwkLoc(float(records[3].split('|')[2]),float(records[3].split('|')[3]),time_stamp,gnd_truth)
				self.nwk_loc_list+=[nwk_loc_reading]

			except Exception :
				continue
	def run_classifier(self,classifier) :
		# main event loop of trace driven simulation
		''' Write into sampling rate vectors before starting '''
		self.current_time=self.event_list[0].time_stamp
		self.accel_sampling_intervals.append((self.current_time,self.accel_interval));
		self.wifi_sampling_intervals.append((self.current_time,self.wifi_interval));
		self.gps_sampling_intervals.append((self.current_time,self.gps_interval));
		self.gsm_sampling_intervals.append((self.current_time,self.gsm_interval));
		self.nwk_loc_sampling_intervals.append((self.current_time,self.nwk_loc_interval));

		while (self.event_list != [] ) :
			current_event=self.event_list.pop(0)
			result=self.subsample(current_event);
			pmf=[0]*5 	# probability dist of ground truth
			pmf[current_event.gnd_truth]=1
			self.gnd_truth+=[(current_event.time_stamp,Distribution(len(pmf),pmf))];
			if (result) :
				''' call back classifier '''
				classifier.callback(current_event,current_event.time_stamp)
				''' update current time now '''
				self.current_time=current_event.time_stamp;
				#print "Current time is ",current_event.time_stamp, " ms, reading is ",current_event
		self.cleanup()
		return (self.accel_sampling_intervals,self.wifi_sampling_intervals,self.gps_sampling_intervals,self.gsm_sampling_intervals,self.nwk_loc_sampling_intervals)

	def run_trainer(self,trainer) :
		# main event loop of trace driven simulation
		while (self.event_list != [] ) :
			
			current_event=self.event_list.pop(0)
			''' call back trainer'''
			trainer.callback(current_event,current_event.time_stamp,current_event.gnd_truth)
			''' update current time now '''
			self.current_time=current_event.time_stamp;
			#print "Current time is ",current_event.time_stamp, " reading is ",current_event
		self.cleanup()

	def cleanup(self) :
		''' clean up simulator and return output '''
		self.accel_sampling_intervals.append((self.current_time,self.accel_interval));
		self.wifi_sampling_intervals.append((self.current_time,self.wifi_interval));		
		self.gps_sampling_intervals.append((self.current_time,self.gps_interval));
		self.gsm_sampling_intervals.append((self.current_time,self.gsm_interval));
		self.nwk_loc_sampling_intervals.append((self.current_time,self.nwk_loc_interval));

	def subsample (self,event) :
		if (isinstance(event,Accel)) :
			if (event.time_stamp >= self.next_accel_timestamp):
				self.next_accel_timestamp+=self.accel_interval;
				return True
		if (isinstance(event,WiFi)) :
			if (event.time_stamp >= self.next_wifi_timestamp):
				self.next_wifi_timestamp+=self.wifi_interval;
				return True
		if (isinstance(event,GPS)) :
			if (event.time_stamp >= self.next_gps_timestamp):
				self.next_gps_timestamp+=self.gps_interval;
				return True
		if (isinstance(event,GSM)) :
			if (event.time_stamp >= self.next_gsm_timestamp):
				self.next_gsm_timestamp+=self.gsm_interval;
				return True
		if (isinstance(event,NwkLoc)) :
			if (event.time_stamp >= self.next_accel_timestamp):
				self.next_nwk_loc_timestamp+=self.nwk_loc_interval;
				return True
