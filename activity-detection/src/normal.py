#! /usr/bin/python
#! learn a normal distribution with support (x>0) and generate it's pdf
from math import *

class Positive_Normal :
	mean=0
	sigma=1

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def __init__ (self,*args) :
		''' Poor man's ML estimation, Ref. to Cohen (1950) for the real thing '''
		if (len(args)==2) :
			self.mean=args[0]
			self.sigma=args[1]
			return
		else :
			value_list=args[0]
		if (value_list==None) :
			return
		(self.mean,variance)=self.mean_and_var(value_list)
		if (variance != None) :
			self.sigma=sqrt(variance)
		else :
			self.sigma=None

	def __str__(self) :
		return "Mean of distribution "+str(self.mean)+" sigma is "+str(self.sigma)

	def pdf(self,x) :
		if (self.mean == None) :
			return 0;
		density=self.phi((x-self.mean)/self.sigma)/self.sigma;
		norm_constant=1-self.Phi((-self.mean)/self.sigma)
		return density/norm_constant

	def phi(self,x) :
		''' the canonical pdf '''
		return exp(-(x**2)/2)/sqrt(2*pi)

	def Phi(self,x) :
		''' the canonical cdf '''
		return (1+erf(x/sqrt(2)))/2

class Normal :
	mean=0
	sigma=1

	def mean_and_var(self,value_list) :
		if (value_list==[]) :
			return (None,None)
		meanSq=reduce(lambda acc,update : acc + update**2,value_list,0.0)/len(value_list)
		mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
		return (mean,meanSq-mean*mean)

	def __init__ (self,*args) :
		''' Poor man's ML estimation, Ref. to Cohen (1950) for the real thing '''
		if (len(args)==2) :
			self.mean=args[0]
			self.sigma=args[1]
			return
		else :
			value_list=args[0]
		if (value_list==None) :
			return
		(self.mean,variance)=self.mean_and_var(value_list)
		if (variance != None) :
			self.sigma=sqrt(variance)
		else :
			self.sigma=None

	def __str__(self) :
		return "Mean of distribution "+str(self.mean)+" sigma is "+str(self.sigma)

	def pdf(self,x) :
		if (self.mean == None) :
			return 0;
		density=self.phi((x-self.mean)/self.sigma)/self.sigma;
		norm_constant=1
		return density/norm_constant

	def phi(self,x) :
		''' the canonical pdf '''
		return exp(-(x**2)/2)/sqrt(2*pi)

	def Phi(self,x) :
		''' the canonical cdf '''
		return (1+erf(x/sqrt(2)))/2
