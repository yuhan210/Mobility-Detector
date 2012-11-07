#! /usr/bin/python
import sys
if (len(sys.argv) < 3 )  :
   print "Usage : downsample.py trace-file sample-interval";
   exit(5);
sensor_trace_file=open(sys.argv[1],"r");
sampling_interval=float(sys.argv[2]);
last_sample=-1.00
for line in sensor_trace_file.readlines() :
 records=line.split(',')
 timestamp=float(records[1])  
 if (last_sample==-1) :
    last_sample=timestamp
    print line.strip() 
 elif (timestamp-last_sample >= sampling_interval) :
    last_sample=timestamp
    print line.strip()

