import matplotlib.pyplot as plt
import numpy as np 
import os


def getTimeStamp(s):
        sSeg = s.split(",")
        timeSeg = sSeg[1].split(".")
        t = long(timeSeg[0])

        return t
def getCurGroundTruth(s):
        seg = s.split("|")
        t = int(seg[3])

        return t


def getTraceLength(filePath, traceGT): # return trace length in seconds
    foo = open(filePath, "r")
    content = foo.readlines()
    totalLength = 0
    for i in range(1,len(content)):
    
        prevTime = getTimeStamp(content[i-1])
        curTime = getTimeStamp(content[i])
        prevGT = getCurGroundTruth(content[i-1])
        curGT =getCurGroundTruth(content[i])

        if prevGT == traceGT and curGT == traceGT and curTime > prevTime :
            totalLength += (curTime - prevTime)
	
    foo.close()
    return float(totalLength/1000)

def getTraceGroundTruth(fileName):
    groundTruth = -1
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
path = 'C:\Users\yuhan\Dropbox\CITA_TESTING_DATA\HTC Inspire_NY'

fListing = os.listdir(path)

for trace in fListing:
    print trace
    
    groundTruth = getTraceGroundTruth(trace)
    for infile in os.listdir(path + '/' + trace):
        if groundTruth == 0 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
        
            
            print infile
            staticTraceLength = staticTraceLength + getTraceLength(path + '/' + trace + '/' + infile, groundTruth)
       
           
        
        if groundTruth == 1 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
           
            print infile
            walkingTraceLength = walkingTraceLength + getTraceLength(path + '/' + trace + '/' + infile, groundTruth)
            
        
        
        if groundTruth == 3 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
             
             print infile
             bikingTraceLength = bikingTraceLength + getTraceLength(path + '/' + trace + '/' + infile, groundTruth)
            
                 
        if groundTruth == 4 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
            
            print infile
            drivingTraceLength = drivingTraceLength + getTraceLength(path + '/' + trace + '/' + infile, groundTruth)
            
         
        if groundTruth == 2 and infile.find('Accel') >= 0 and os.path.isdir(infile) == False:
            
            print infile
            runningTraceLength = runningTraceLength + getTraceLength(path + '/' + trace + '/' + infile, groundTruth)
            
         
        

print "static(hrs):" + str(staticTraceLength/3600)
print "walking(hrs):" + str(walkingTraceLength/3600)
print "running(hrs):" + str(runningTraceLength/3600)
print "biking(hrs):" + str(bikingTraceLength/3600)
print "driving(hrs):"+ str(drivingTraceLength/3600)
