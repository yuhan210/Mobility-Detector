'- Make sure all traces have monotonically increasing timestamp'
'- '
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


'1. Keep the segment which has the correct groundtruth'
'2. Remove the first 2 mins'
'3. Split traces if timestamp has a gap'
'4. Split traces into 15mins chuncks'
def getTraceIndexPairs(accelFilePath):
	traceGT = getTraceGroundTruth(accelFilePath)
	cleanTraceIndexPairs = [] # trace with correct groundtruth
	monoIncreaseTraceIndexPairs = [] 
	
	accelFile = open(accelFilePath, "r")
	content = accelFile.readlines()
	
	
	# get clean trace segments (might still have time gaps)
	pairDict = {}
	prevGT = -1
	for i in range(len(content)):
		line = content[i]
		curTime = getTimeStamp(line)
		curGT = getCurGroundTruth(line)				
		
		if prevGT != traceGT and curGT == traceGT:
			pairDict = {}
			pairDict['startIndex'] = i
			pairDict['startTime'] = getTimeStamp(line)
			
		elif curGT != traceGT and prevGT == traceGT:
			pairDict['endIndex'] = (i-1)
			pairDict['endTime'] = getTimeStamp(content[(i-1)])
			cleanTraceIndexPairs.append(pairDict)
			
		prevGT = curGT
	
	## 
	if (pairDict.has_key('startIndex')) and (not pairDict.has_key('endIndex')):
		pairDict['endIndex'] = len(content) - 1
		pairDict['endTime'] = getTimeStamp(content[len(content)-1])
		cleanTraceIndexPairs.append(pairDict)

	cleanTraceIndexPairs.sort(key=operator.itemgetter('startIndex'))

	## cut the first 2mins of the first segment
	CUT_OF_TIME = 2 * 60 * 1000
	startTime = cleanTraceIndexPairs[0]['startTime']
	if cleanTraceIndexPairs[0]['endTime'] - cleanTraceIndexPairs[0]['startTime'] >= CUT_OF_TIME:
		for i in xrange(cleanTraceIndexPairs[0]['startIndex'], cleanTraceIndexPairs[0]['endIndex']):
			if getTimeStamp(content[i]) - startTime >= CUT_OF_TIME:
				cleanTraceIndexPairs[0]['startTime'] = getTimeStamp(content[i])
				cleanTraceIndexPairs[0]['startIndex'] = i
				break
	else:
		cleanTraceIndexPairs.pop(0)
	print "cleanTraceIndexPairs", cleanTraceIndexPairs	


	#find time jumps within each clean trace segment
	pairDict = {}
	TRACE_BLOCK_LENGTH = 15 * 60 * 1000
	for cleanPair in cleanTraceIndexPairs:
		startIndex = cleanPair['startIndex']
		endIndex = cleanPair['endIndex']

		
		pairDict['startIndex'] = startIndex
		pairDict['startTime'] = cleanPair['startTime']
		prevTime = cleanPair['startTime']
		for i in xrange(startIndex + 1,endIndex + 1):
					
			line = content[i]
			curTime = getTimeStamp(line)
			if curTime < prevTime or (curTime - pairDict['startTime']) > TRACE_BLOCK_LENGTH:
				pairDict['endIndex'] = (i-1)
				pairDict['endTime'] = getTimeStamp(content[(i-1)])
				pairDict['length'] = (pairDict['endTime'] - pairDict['startTime'])/ (1000*60*1.0)
				monoIncreaseTraceIndexPairs.append(pairDict)
				pairDict = {}
				pairDict['startIndex'] = i
				pairDict['startTime'] = getTimeStamp(content[i])
			
			prevTime = curTime	
		

		if (pairDict.has_key('startIndex')) and (not pairDict.has_key('endIndex')):
		
			pairDict['endIndex'] = i
			pairDict['endTime'] = getTimeStamp(content[i])	
			pairDict['length'] = (pairDict['endTime'] - pairDict['startTime'])/ (1000*60*1.0)
			monoIncreaseTraceIndexPairs.append(pairDict)					
	
	monoIncreaseTraceIndexPairs.sort(key=operator.itemgetter('startIndex'))
	
	accelFile.close()
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

'Generate the folders according to the pairDict'
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
			
			for line in content:
				curTime = getTimeStamp(line)
				
				if pairCounter == 0:## the timing to open a new file
					if (curTime >= pairDict[pairCounter]['startTime']):
						filePath = newRoot + getReadableTime(pairDict[pairCounter]['startTime']) + "_" + activity + "/" + sensor + getReadableTime(pairDict[pairCounter]['startTime'])
						print filePath + " created."
						pairCounter += 1
						newFile = open(filePath,"w")
						
				elif pairCounter > 0 and pairCounter < len(pairDict):
					if (prevTime >= curTime) or ((curTime > pairDict[pairCounter-1]['endTime']) and (curTime >= pairDict[pairCounter]['startTime'])):
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
								


if __name__ == "__main__":
	##  Process input
	if (len(sys.argv) < 2):
		print "Usage: traceSanitizer.py trace_folder dest_folder_path"
		exit(5)

	tracePath = sys.argv[1]
	destPath = sys.argv[2]
	
	## Prelim process
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
