#! /usr/bin/python
from distributions import *
# represent an interval
class Interval(object) :	# Represents a closed Interval in time along with a Distribution of states valid over that interval
	start=0
	end=0
	distribution=Distribution(5,[0]*5)
	def get_length(self) :
		return self.end-self.start
	def __init__ (self,start,end,distribution) :
		self.start=start
		self.end=end
		self.distribution=distribution
	def __str__(self) :
		return "Interval: start "+str(self.start)+" ms, end "+str(self.end)+" ms, distribution "+str(self.distribution)
	def __repr__(self) :
		return str(self)
	def get_overlap(self,interval) :
		if   ((interval.start >= self.end) or (interval.end <= self.start)) :   # outside
			return 0
		elif ((interval.start >= self.start) and (interval.end <= self.end) ) : # engulfed
			return interval.get_length()
		elif ((interval.start <= self.start) and (interval.end >= self.end) ) : # engulfing
			return self.get_length()
		elif ((interval.start <= self.start) and (interval.end <= self.end) ) : # left overlap
			return interval.end-self.start
		elif ((interval.start >= self.start) and (interval.end >= self.end) ) : # right overlap
			return self.end-interval.start
