#! /usr/bin/python
from markov import *
from trace import *
''' Program to stitch traces together into a larger trace '''
import sys
from os import *
from os.path import *
if ( len(sys.argv) < 8) :
	print "Usage : python ",sys.argv[0]," duration_in_ms static_trace_folder walking_trace_folder running_trace_folder biking_trace_folder driving_trace_folder random_seed "
	exit(5)
else :
	duration=int(sys.argv[1]);
	static_trace_folder=sys.argv[2]
	walking_trace_folder=sys.argv[3]
	running_trace_folder=sys.argv[4]
	biking_trace_folder=sys.argv[5]
	driving_trace_folder=sys.argv[6]

	''' Extract traces from folders '''	
	# a list of traces
	static_traces =  map(lambda x : Trace (join(static_trace_folder,x))  ,
			filter(lambda x : isfile(join(static_trace_folder,x)) ,listdir(static_trace_folder)))
	walking_traces=  map(lambda x : Trace (join(walking_trace_folder,x)) ,
			filter(lambda x : isfile(join(walking_trace_folder,x)),listdir(walking_trace_folder)))
	running_traces=  map(lambda x : Trace (join(running_trace_folder,x)) ,
			filter(lambda x : isfile(join(running_trace_folder,x)),listdir(running_trace_folder)))
	biking_traces =  map(lambda x : Trace (join(biking_trace_folder,x))  ,
			filter(lambda x : isfile(join(biking_trace_folder,x)) ,listdir(biking_trace_folder)))
	driving_traces=  map(lambda x : Trace (join(driving_trace_folder,x)) ,
			filter(lambda x : isfile(join(driving_trace_folder,x)),listdir(driving_trace_folder)))

	''' Indices to keep track of which trace file to write next '''
	static_index =0
	walking_index=0
	running_index=0
	biking_index =0
	driving_index=0

	random_seed=int(sys.argv[7]);
	m=MarkovChain(random_seed,['static','walking','running','biking','driving'])
	sampled_dtmc=m.simulate(duration);
	for i in range(0,len(sampled_dtmc)) :
		current=sampled_dtmc[i]
		if ( i < len(sampled_dtmc) -1 ) :
			next_change=sampled_dtmc[i+1]
			end=next_change[0]
		else :
			end=duration
		start=current[0]
		current_activity=current[1]
		if ( current_activity == 0 ):
			static_traces[static_index].rewrite_trace_file(start,end);
			print "Using static_index ",static_index
			static_index=(static_index+1)%len(static_traces)
		elif ( current_activity == 1 ):
			walking_traces[walking_index].rewrite_trace_file(start,end);
			print "Using walking_index ",walking_index
			walking_index=(walking_index+1)%len(walking_traces)
		elif ( current_activity == 2 ):
			running_traces[running_index].rewrite_trace_file(start,end);
			print "Using running_index ",running_index
			running_index=(running_index+1)%len(running_traces)
		elif ( current_activity == 3 ):
			biking_traces[biking_index].rewrite_trace_file(start,end);
			print "Using biking_index ",biking_index
			biking_index=(biking_index+1)%len(biking_traces)
		elif ( current_activity == 4 ):
			driving_traces[driving_index].rewrite_trace_file(start,end);
			print "Using driving_index ",driving_index
			driving_index=(driving_index+1)%len(driving_traces)
