import os
import sys
import datetime
import operator
import shutil

def getTimeStamp(s):
	sSeg = s.split(",")
	timeSeg = sSeg[1].split(".")
	t = long(timeSeg[0])	
	
	return t
def getCurGroundTruth(s):
	seg = s.split("|")
	t = int(seg[3])
		
	return t

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


def getTraceIndexPairs(accelFilePath):
	traceGT = getTraceGroundTruth(accelFilePath)
	cleanTraceIndexPairs = [] # trace with correct groundtruth
	monoIncreaseTraceIndexPairs = [] 
	
	accelFile = open(accelFilePath, "r")
	content = accelFile.readlines()
	
	pairDict = {}	
	
	# get clean trace segments (might still have time jumps)
	prevGT = -1
	for i in range(len(content)):
		line = content[i]
		curTime = getTimeStamp(line)
		curGT = getCurGroundTruth(line)				
		
		if prevGT != traceGT and curGT == traceGT:
			pairDict['startIndex'] = i
			pairDict['startTime'] = getTimeStamp(line)
			
		elif curGT != traceGT and prevGT == traceGT:
			pairDict['endIndex'] = (i-1)
			pairDict['endTime'] = getTimeStamp(content[(i-1)])
			cleanTraceIndexPairs.append(pairDict)
			pairDict = {}
			
		prevGT = curGT	
	
	if (pairDict.has_key('startIndex')) and (not pairDict.has_key('endIndex')):
		pairDict['endIndex'] = i
		pairDict['endTime'] = getTimeStamp(content[i])
		cleanTraceIndexPairs.append(pairDict)
	print cleanTraceIndexPairs	


	#find time jumps within each clean trace segment
	pairDict = {}
	for dictPair in cleanTraceIndexPairs:
		startIndex = dictPair['startIndex']
		endIndex = dictPair['endIndex']
		prevTime = dictPair['startTime']
		
		pairDict['startIndex'] = startIndex
		pairDict['startTime'] = dictPair['startTime']

		for i in range(startIndex+1,endIndex + 1):
					
			line = content[i]
			curTime = getTimeStamp(line)
			if curTime <= prevTime:
				pairDict['endIndex'] = (i-1)
				pairDict['endTime'] = getTimeStamp(content[(i-1)])
				monoIncreaseTraceIndexPairs.append(pairDict)
				pairDict = {}
				pairDict['startIndex'] = i
				pairDict['startTime'] = getTimeStamp(content[i])
			
			prevTime = curTime	
		

		if (pairDict.has_key('startIndex')) and (not pairDict.has_key('endIndex')):
		
			pairDict['endIndex'] = i
			pairDict['endTime'] = getTimeStamp(content[i])	
			monoIncreaseTraceIndexPairs.append(pairDict)					
	
	accelFile.close()
	monoIncreaseTraceIndexPairs.sort(key=operator.itemgetter('startIndex'))
	return monoIncreaseTraceIndexPairs

def getReadableTime(t):

	dt = datetime.datetime.fromtimestamp(int(t/1000))
	timeStr = dt.strftime("%Y-%m-%d-%H-%M-%S")
	
	return timeStr	

def getSensorFromFileName(fName):
	sensor = "nop"
	if fName.find("Accel") >= 0:
		sensor = "Accel"
	elif fName.find("GPS") >= 0:
		sensor = "GPS"
	elif fName.find("GSM") >= 0:
		sensor = "GSM"
	elif fName.find("Wifi") >= 0:
		sensor = "Wifi"
	elif fName.find("Geo Loc") >= 0:
		sensor = "Geo Loc"
	return sensor

def createCleanTraces(tracePath, destPath, pairDict):

	pathSeg = tracePath.split("/")
	user = pathSeg[-2]
	trace = pathSeg[-1]
	activitySeg =  trace.split("_")
	activity = activitySeg[1]
	newRoot = destPath + "/" + user +"/" + activity	+ "/"

	## create all new directories
	for i in range(len(pairDict)):
			
		startTime = pairDict[i]['startTime']
		newTraceFolderPath = newRoot + getReadableTime(startTime) + "_" + activity
	
		if not os.path.exists(newTraceFolderPath):
			os.makedirs(newTraceFolderPath)	

	## create files	
	sensorListing = os.listdir(tracePath)
	for sensorFile in sensorListing:
		sensor = getSensorFromFileName(sensorFile)
		if sensor.find("nop") == -1:
			print sensorFile
			orgFile = open(tracePath + "/" + sensorFile, "r")
			
			pairCounter = 0
			prevTime = 0
			content = orgFile.readlines()
			if len(content) == 0:
				print "file's empty"
				continue
			
			
			newFile = ""
			for line in content:
				curTime = getTimeStamp(line)
				
				if pairCounter == 0:
					if (curTime >= pairDict[pairCounter]['startTime']):
							
						filePath = newRoot + getReadableTime(pairDict[pairCounter]['startTime']) + "_" + activity + "/" + sensor + getReadableTime(pairDict[pairCounter]['startTime'])
						print filePath + " created."
						pairCounter += 1
						newFile = open(filePath,"w")
						
				elif pairCounter > 0 and pairCounter < len(pairDict):
					if (prevTime >= curTime) or ((curTime > pairDict[pairCounter-1]['endTime']) and (curTime >= pairDict[pairCounter]['startTime'])):
						#print "prevTime:" + str(prevTime) +",curTime" + str(curTime)
						#print pairCounter
						newFile.close()	
						filePath = newRoot + getReadableTime(pairDict[pairCounter]['startTime']) + "_" + activity + "/" + sensor + getReadableTime(pairDict[pairCounter]['startTime'])
						print filePath + " created."
						pairCounter += 1
						newFile = open(filePath,"w")
				
				if pairCounter > 0 and curTime >= pairDict[pairCounter - 1]['startTime'] and curTime <= pairDict[pairCounter-1]['endTime']:
					newFile.write(line)
					
				prevTime = curTime	
			newFile.close()	
			orgFile.close()					
								



##  Process input
if (len(sys.argv) < 2):
	print "Usage: traceSanitizer.py trace_folder dest_folder_path"
	exit(5)

tracePath = sys.argv[1]
destPath = sys.argv[2]

if tracePath[-1] == "/":
	tracePath = tracePath[:-1]

if destPath[-1] == "/":
	destPath = destPath[:-1]

## find all the time bumps 

sensorListing = os.listdir(tracePath)
for sensorFile in sensorListing:
	if sensorFile.find("Accel") >= 0:
			
		indexPairs = getTraceIndexPairs(tracePath + "/" + sensorFile)		
		print indexPairs

if len(indexPairs) > 0:
	createCleanTraces(tracePath,destPath,indexPairs)
