import os
from math import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import Image

def mean_and_std(value_list) :
	if (value_list==[]) :
		return (None,None)
	
	mean=reduce(lambda acc,update : acc + update,value_list,0.0)/len(value_list)
	std = 0
	for i in value_list:
		std += (i - mean) * (i -mean)
	
	if len(value_list) < 2:
		std = 0
	else:
		std = sqrt(std/(len(value_list)-1))	
		
	return (mean,std)


path = "seeds"
x = [1,10,20,30,40,50,60,70,80,90,100]
hard_match = []
soft_match = []

hmean = []
hstd = []

smean = []
sstd = []

for i in range(len(x)):
	hard_match.append([])
	soft_match.append([])

seedListing = os.listdir(path)
for seedFolder in seedListing:
	fileListing = os.listdir(path + "/" + seedFolder)
	
	for f in fileListing:
		if f.find("stderr.out") >= 0:
			foo = open(path+"/" + seedFolder + "/" + f,"r")
			
			for line in foo.readlines():
				accuracy = 0
				if line.find("Hard match") >= 0:
					accuracy = float(line.split(" ")[3])
					if int(f.split("_")[0]) == 1:
						 hard_match[0].append(accuracy)

					elif int(f.split("_")[0]) >= 10:
						hard_match[(int(f.split("_")[0])/10)].append(accuracy)
				
				if line.find("Soft match") >= 0:
					accuracy = float(line.split(" ")[3])
					if int(f.split("_")[0]) == 1:
						 soft_match[0].append(accuracy)

					elif int(f.split("_")[0]) >= 10:
						soft_match[(int(f.split("_")[0])/10)].append(accuracy)
				

for i in range(len(x)):
	(mean,std) = mean_and_std(hard_match[i])
	hmean.append(mean)				
	hstd.append(std)

	(mean,std) = mean_and_std(soft_match[i])
	smean.append(mean)				
	sstd.append(std)

print hmean
print smean

fig = plt.figure()
plt.errorbar(x, hmean, yerr=hstd, fmt='bo-')
plt.errorbar(x, smean, yerr=sstd, fmt='ro-')


plt.title("Give me a tradeoff")
fig.savefig('result.png')
