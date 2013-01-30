#! /usr/bin/python
''' Represent discrete distributions in Python '''
class Distribution(object) :
	num_states=5 	# number of discrete states
	pmf=[]		# probability mass function
	def __init__(self,num_states,pmf):
		assert (num_states == len(pmf))
		self.num_states=num_states
		self.pmf=pmf
	def __str__(self) :
		return "Number of states " + str(self.num_states) + " mode " + str(self.mode()) + " pmf : "+str(self.pmf)+ "\n"
	def __repr__(self) :
		return self.__str__()
	def __eq__(self,other) :
		if (self.num_states != other.num_states) :
			return False
		else :
			return ( self.pmf == other.pmf )
	def __ne__(self,other) :
		return not (self.__eq__(other))
	def mode (self) :
		return self.pmf.index(max(self.pmf))
	def __mul__(self,other) :	# dot product
		return reduce(lambda acc,update : acc+update[0]*update[1],zip(self.pmf,other.pmf),0.0)
