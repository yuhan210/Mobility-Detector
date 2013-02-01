#! /usr/bin/python
''' Class that represents a trace file '''
class Trace(object) :
	trace_file=""
	start_time=-1;
	end_time=-1;
	trace_in_mem=[];
	sensor_dict=['Accel','Wifi','GPS','GSM','Geo Loc']
	stitched_file_handle = open("stitched-trace.out","w")

	def __init__(self,trace_file): 
		self.trace_file=trace_file;
		fh=open(self.trace_file,"r");
		print self.trace_file
		for line in fh.readlines():
			ts_milli=int(float(line.split(',')[1]))
			if ( ( self.start_time == -1) or (ts_milli < self.start_time) ) :
				self.start_time=ts_milli
			if ( ( self.end_time   == -1) or (ts_milli >   self.end_time) ) :
				self.end_time  =ts_milli
			self.trace_in_mem+=[(ts_milli,line)]
		self.trace_in_mem.sort(key=lambda x: x[0])

	def calc_length(self) :
		return self.end_time-self.start_time

	def rewrite_trace_file(self,start,end):
		time_written_out=start
		print "start of new activity is ",start, " and end is ",end, "length:", (end-start)/(60 * 1000 *1.0) ,"mins", "trace length:",self.calc_length()/(60 * 1000 * 1.0)
		while ( time_written_out < end ) :
			''' write out the list to a file in epochs until exhausted '''
			epoch_start=time_written_out
			epoch_end  =min(time_written_out+self.calc_length(),end)
			for line in self.trace_in_mem :
			
				actual_ts = line[0]
				if ( ((actual_ts-self.start_time) >= 0 ) and 
				     ((actual_ts-self.start_time) <= epoch_end - epoch_start  )) :
					mod_ts=actual_ts-self.start_time+epoch_start;
					records=line[1].split(',')
					new_line=records[0]+","+str(mod_ts); # ts are in ms
					for i in range (2,len(records)) :
						new_line+=","+records[i]
					self.stitched_file_handle.write(new_line)
			time_written_out=epoch_end
