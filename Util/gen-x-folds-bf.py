from itertools import combinations
import os
import sys
import shutil

W = [2,3,4,5,6]
SUM = 15

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
       
def getList(M, SUM):
	result = []
	for r in range(1, len(W)+1):
		for comb in combinations(W,r):
			if sum(list(comb)) == SUM:
				result+= [list(comb)]
	return result

def getTraceLengthDict(root):
	traceDict = {}
	for i in xrange(5):
		traceDict[i] = []

	userListing = os.listdir(root)
	for user in userListing:
		userDirPath = root + "/" + user
		folderListing = os.listdir(userDirPath)
		for activity in folderListing:
			activityDirPath = userDirPath + "/" + activity
			traceListing = os.listdir(activityDirPath)
			for trace in traceListing:
				trace_gnd = getTraceGroundTruth(trace)	
				traceDirPath = activityDirPath + "/" + trace
				sensorListing = os.listdir(traceDirPath)
				for sensor in sensorListing:
					if sensor.find("Accel") >= 0:
						length = getTraceLength(traceDirPath+ "/"+sensor, trace_gnd)
						
						if length < 1: # the trace is too short, remove it
							shutil.rmtree(traceDirPath)						
						
						name_length_pair = {}
						name_length_pair['path'] = traceDirPath
						name_length_pair['length'] =length # in sec
										
						traceDict[trace_gnd].append(name_length_pair)
	return traceDict
def compute_activity_total_time(traceDict):
	activity_total_length = []
	for i in xrange(5):
		activity_total_length.append(0)

	for activity in traceDict:
		for trace in traceDict[activity]:
			activity_total_length[activity] += trace['length']	
	return activity_total_length

def getActivity(i):
	act = ['s','w','r','b','d']
	return act[i]

def genFolds(fold_num, target_length, traceDict,delta,dest_root):

	delta = delta # sec, allowing 2*delta time of difference	
	print "target_length", target_length
	for i in xrange(fold_num):
		folder = str(i+1)
		if not os.path.exists(root+"/"+ folder): 
			os.makedirs(root+"/"+ folder)	
		if not os.path.exists(root+"/"+folder+"/s"):
			os.makedirs(root+"/"+ folder + "/s")	
		if not os.path.exists(root+"/"+folder+"/w"):
			os.makedirs(root+"/"+ folder + "/w")	
		if not os.path.exists(root+"/"+folder+"/b"):
			os.makedirs(root+"/"+ folder + "/b")	
		if not os.path.exists(root+"/"+folder+"/r"):
			os.makedirs(root+"/"+ folder + "/r")	
		if not os.path.exists(root+"/"+folder+"/d"):
			os.makedirs(root+"/"+ folder + "/d")
	
	for activity in traceDict:
		
		trace_num = len(traceDict[activity])

		possible_trace_comb = []
		for r in range(1, trace_num +1):
			for comb in combinations(traceDict[activity],r):
				cur_comb_total_time = 0
				for trace in list(comb):
					cur_comb_total_time += trace['length']
				
				if cur_comb_total_time > (target_length - delta) and cur_comb_total_time < (target_length + delta):
					possible_trace_comb.append(map(lambda x: x['path'], list(comb)))
					#possible_trace_comb.append(list(comb))
				
		print possible_trace_comb
		file_for_each_folder = removeDupTrace(possible_trace_comb, fold_num)	

		for i in xrange(len(file_for_each_folder)):	
			# cp files
			for f in file_for_each_folder[i]:
				new_file_name = f.split("/")[-1]
				activity_dir = getActivity(activity)
				print dest_root+"/"+str(i+1)+"/"+activity_dir+"/"+new_file_name
				shutil.copy(f, dest_root+"/"+str(i)+"/"+activity_dir+"/"+f)
				
		
def removeDupTrace(possible_trace_comb, fold_num):
	if len(possible_trace_comb) < fold_num:
		print "The number of possible combinations", len(possible_trace_comb), " is less than the fold_num", fold_num
		exit(5)
	elif len(possible_trace_comb) == fold_num:
		return possible_trace_comb

	else:# the number of possible comb is more than you needed, choose the best one
		for i in xrange(len(possible_trace_comb)):
			for comb in combinations(possible_trace_comb,fold_num): 	
				result = reduce(set.intersection,map(set,list(comb)))	
				if len(result) == i:
					return list(comb)



if __name__ == "__main__":
	if (len(sys.argv) < 4):
		print "Usage: all-user-dir fold-num dest-folder delta"
		exit(5)


	root = sys.argv[1]
	fold_num = int(sys.argv[2])
	dest_path = sys.argv[3]
	delta = int(sys.argv[4])

	traceDict = getTraceLengthDict(root) # a dict(activity) of a list of dict(filename, length)
	
	activity_total_length = compute_activity_total_time(traceDict)
	print activity_total_length.sort()
	activity_length_for_each_folder =  activity_total_length[1]/(fold_num * 1.0)
	
	genFolds(fold_num, activity_length_for_each_folder, traceDict, delta, dest_path)
	#print activity_total_length	
	
	#for activity in traceDict:
			
	
	
W = [2,3,4,5,6]
SUM = 15
