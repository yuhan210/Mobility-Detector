#! /usr/bin/python
import sys
file_handle=sys.stdin
sensor_type=sys.argv[1]
for line in file_handle.readlines() :
	# find gnd truth
	if (sensor_type == "Accel") :
		records=line.split(',')
		try :
			time_stamp=int(float(records[1]))
			gnd_truth=int(records[3].split('|')[3])
			accel_reading=Accel(float(records[3].split('|')[0]),float(records[3].split('|')[1]),float(records[3].split('|')[2]),time_stamp,gnd_truth)
			self.accel_list+=[accel_reading]
			print ",".join(records[1:2]),",Accel,",
		except Exception :
			continue

	elif (sensor_type == "WiFi") :
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
			print ",".join(records[1:2]),",Wifi,",
		except Exception :
			continue


	elif (sensor_type == "GPS") :
		try :
			records=line.split(',')
			time_stamp=int(float(records[1]))
			gnd_truth=int(records[3].split('|')[8])
			gps_reading=GPS(float(records[3].split('|')[2]),float(records[3].split('|')[3]),time_stamp,gnd_truth)
			self.gps_list+=[gps_reading]
			print ",".join(records[1:2]),",GPS,",'|'.join(records[3].split('|')[len(records[3].split('|')-1],"|",indoor_or_outdoor
		except Exception :
			continue

	
	elif (sensor_type == "GSM") :
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
			print ",".join(records[1:2]),",GSM,",'|'.join(records[3].split('|')[:5],"|",indoor_or_outdoor,'|'.join(records[3].split('|')[6:]
			
		except Exception :
			continue
	
	elif (sensor_type == "Geo Loc"):
		try :
			records=line.split(',')
			time_stamp=int(float(records[1]))
			gnd_truth=int(records[3].split('|')[8])
			nwk_loc_reading=NwkLoc(float(records[3].split('|')[2]),float(records[3].split('|')[3]),time_stamp,gnd_truth)
			self.nwk_loc_list+=[nwk_loc_reading]
			print ",".join(records[1:2]),",Geo Loc,",'|'.join(records[3].split('|')[len(records[3].split('|')-1],"|",indoor_or_outdoor
		except Exception :
			continue

	else :
		exit(5);
