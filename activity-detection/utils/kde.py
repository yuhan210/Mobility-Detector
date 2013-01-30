from scipy.stats.kde import gaussian_kde
import matplotlib.pyplot as plt
from numpy import *
from scipy.stats import norm
import numpy
import pickle
fh=open('test_list','r')
feature_list = pickle.load(fh);
x = linspace(min(feature_list),max(feature_list),300)

''' trunc_pdf 60% slower than scipy.stats.gaussian_kde '''
bw=0.003
samples=array(feature_list)
sf_array=(norm.sf((-samples)/bw))
norm_constant=bw*len(samples)
sample_length=len(samples)
def trunc_pdf (x) :
	x_repeated=array([x]*sample_length)
	norm_pdfs=norm.pdf((x_repeated-samples)/bw)/sf_array
	return numpy.sum(norm_pdfs)/norm_constant
plt.plot(x,map(lambda y : trunc_pdf(y), x ),'r')

''' untrunc_pdf 30% slower than scipy.stats.gaussian_kde '''
def untrunc_pdf (x) :
	x_repeated=array([x]*sample_length)
	norm_pdfs=norm.pdf((x_repeated-samples)/bw)
	return numpy.sum(norm_pdfs)/norm_constant
plt.plot(x,map(lambda y : untrunc_pdf(y), x ),'g')

''' scipy.stats.gaussian_kde '''
kernel_pdf = gaussian_kde(feature_list)
plt.plot(x,kernel_pdf(x),'b')

''' actual data '''
plt.plot(feature_list,[0.1]*len(feature_list),"x")
plt.show()
