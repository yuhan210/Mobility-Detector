import matplotlib.pyplot as plt
import numpy as np 
import os

def getTraceLength(file): # return trace length in seconds
    firstTimeStamp = 0
    lastTimeStamp = 0
    for line in file:
        tSeg = line.split(",")
        curTimeStampSeg = tSeg[1].split(".") # time in milli second
        lastTimeStamp = float(curTimeStampSeg[0])
                
        if firstTimeStamp == 0:
            firstTimeStamp = lastTimeStamp
	
    length = (lastTimeStamp - firstTimeStamp)/1000
    return length

def getGroundTruth(fileName):
    if(fileName.find('static') >= 0):
        groundTruth = 0
    if(fileName.find('walking') >= 0):
        groundTruth = 1
    if(fileName.find('running') >= 0):
        groundTruth = 2
    if(fileName.find('biking') >= 0):
        groundTruth = 3
    if(fileName.find('driving') >= 0):
        groundTruth = 4
    return groundTruth
       
staticTraceLength = 0
walkingTraceLength = 0
runningTraceLength = 0
bikingTraceLength = 0
drivingTraceLength = 0
path = 'C:\Users\yuhan\Dropbox\CITA_DATA\Somak'

fListing = os.listdir(path)

for trace in fListing:
    print trace
    
    groundTruth = getGroundTruth(trace)
    for infile in os.listdir(path + '/' + trace):
        if groundTruth == 0 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
        
            foo = open(path + '/' + trace + '/' + infile)
            print infile
            staticTraceLength = staticTraceLength + getTraceLength(foo)
       
            foo.close()
        
        if groundTruth == 1 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
            foo = open(path + '/' + trace + '/' + infile)
            print infile
            walkingTraceLength = walkingTraceLength + getTraceLength(foo)
            foo.close()
        
        
        if groundTruth == 3 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
             foo = open(path + '/' + trace + '/' + infile)
             print infile
             bikingTraceLength = bikingTraceLength + getTraceLength(foo)
             foo.close()
                 
        if groundTruth == 4 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
            foo = open(path + '/' + trace + '/' + infile)
            print infile
            drivingTraceLength = drivingTraceLength + getTraceLength(foo)
            foo.close()
         
        if groundTruth == 2 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
            foo = open(path + '/' + trace + '/' + infile)
            print infile
            runningTraceLength = runningTraceLength + getTraceLength(foo)
            foo.close()
         
        

print staticTraceLength/3600
print walkingTraceLength/3600
print runningTraceLength/3600
print bikingTraceLength/3600
print drivingTraceLength/3600
