#! /usr/bin/python
import sys
import math

if (len(sys.argv) < 3 )  :
   print "Usage : downsample.py trace-file sample-interval";
   exit(5);

sensor_trace_file=open(sys.argv[1],"r");
sampling_interval=float(sys.argv[2]);

last_sample=-1.0
content = sensor_trace_file.readlines()
for i in range(len(content)) :
 line = content[i]
 records=line.split(',')
 timestamp=float(records[1])/1.0e3 
 
 if (last_sample==-1) :
    last_sample=timestamp
    print line.strip() 
 elif (timestamp-last_sample >= sampling_interval):
    
    prevLine = content[(i-1)]
    prevRecords = prevLine.split(',')
    prevTimeStamp = float(prevRecords[1])/1.0e3
    
    if( abs((abs(last_sample - prevTimeStamp)) - sampling_interval) < abs((abs(timestamp - last_sample)) - sampling_interval)):
	
    	last_sample = prevTimeStamp
	print prevLine.strip()
    else:
	last_sample = timestamp
        print line.strip()

