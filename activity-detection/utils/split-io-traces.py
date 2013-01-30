#! /usr/bin/python
import sys
file_handle=sys.stdin
last_gnd_truth=-1
current_file_handle=0
name={ 0:"unknown_templates", 1:"indoor_templates" , 2: "outdoor_templates" }
counter={ 0:0, 1:0, 2:0 }
def write_to_new_file(current_file_handle,name,counter,gnd_truth,last_gnd_truth) :
	if (gnd_truth != last_gnd_truth) :
		counter[gnd_truth]+=1;
		current_file_handle=open("./"+name[gnd_truth]+"/"+str(counter[gnd_truth])+".out","w");
		last_gnd_truth=gnd_truth;
	current_file_handle.write(line);
	return (current_file_handle,name,counter,last_gnd_truth)

for line in file_handle.readlines() :
	# find gnd truth
	sensor_type=line.split(',')[2]
	records=line.split(',')
	assert (sensor_type == "Wifi") 
	try :
		gnd_truth=int(records[3].split('|')[5])
	except Exception :
		continue
	(current_file_handle,name,counter,last_gnd_truth)=write_to_new_file(current_file_handle,name,counter,gnd_truth,last_gnd_truth)
