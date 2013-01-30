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

	static_trace_count  = [0] * len(static_traces)
	walking_trace_count = [0] * len(walking_traces)
	running_trace_count = [0] * len(running_traces)
	biking_trace_count  = [0] * len(biking_traces)
	driving_trace_count = [0] * len(driving_traces)

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
			
			static_candidate_index = []
			for i in xrange(len(static_trace_count)):
				if static_trace_count[i] == min(static_trace_count):
					static_candidate_index+=[i]
			
			min_length_diff =  min(map(lambda x: abs(static_traces[x].calc_length() - (end-start)),static_candidate_index))
		
			for static_index in static_candidate_index:
				if abs(static_traces[static_index].calc_length() - (end-start)) == min_length_diff:
					break
			
			static_trace_count[static_index]+=1
			static_traces[static_index].rewrite_trace_file(start,end);
			print "Using static_index ",static_index
		elif ( current_activity == 1 ):

			walking_candidate_index = []
			for i in xrange(len(walking_trace_count)):
				if walking_trace_count[i] == min(walking_trace_count):
					walking_candidate_index+=[i]
			
			min_length_diff =  min(map(lambda x: abs(walking_traces[x].calc_length() - (end-start)),walking_candidate_index))
		
			for walking_index in walking_candidate_index:
				if abs(walking_traces[walking_index].calc_length() - (end-start)) == min_length_diff:
					break
			
			walking_trace_count[walking_index]+=1
			walking_traces[walking_index].rewrite_trace_file(start,end);
			print "Using walking_index ",walking_index
		elif ( current_activity == 2 ):
		
			running_candidate_index = []
			for i in xrange(len(running_trace_count)):
				if running_trace_count[i] == min(running_trace_count):
					running_candidate_index+=[i]
			
			min_length_diff =  min(map(lambda x: abs(running_traces[x].calc_length() - (end-start)),running_candidate_index))
		
			for running_index in running_candidate_index:
				if abs(running_traces[running_index].calc_length() - (end-start)) == min_length_diff:
					break
			
			running_trace_count[running_index]+=1
			running_traces[running_index].rewrite_trace_file(start,end);
			print "Using running_index ",running_index
		
		elif ( current_activity == 3 ):
		
			biking_candidate_index = []
			for i in xrange(len(biking_trace_count)):
				if biking_trace_count[i] == min(biking_trace_count):
					biking_candidate_index+=[i]
			
			min_length_diff =  min(map(lambda x: abs(biking_traces[x].calc_length() - (end-start)),biking_candidate_index))
		
			for biking_index in biking_candidate_index:
				if abs(biking_traces[biking_index].calc_length() - (end-start)) == min_length_diff:
					break
			
			biking_trace_count[biking_index]+=1
			biking_traces[biking_index].rewrite_trace_file(start,end);
			print "Using biking_index ",biking_index
		
		elif ( current_activity == 4 ):
			driving_candidate_index = []
			for i in xrange(len(driving_trace_count)):
				if driving_trace_count[i] == min(driving_trace_count):
					driving_candidate_index+=[i]
			
			min_length_diff =  min(map(lambda x: abs(driving_traces[x].calc_length() - (end-start)),driving_candidate_index))
		
			for driving_index in driving_candidate_index:
				if abs(driving_traces[driving_index].calc_length() - (end-start)) == min_length_diff:
					break
			
			driving_trace_count[driving_index]+=1
			driving_traces[driving_index].rewrite_trace_file(start,end);
			print "Using driving_index ",driving_index
