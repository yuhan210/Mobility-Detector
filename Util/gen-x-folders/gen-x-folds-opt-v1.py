'Divide traces into x folds, and each fold has approximately the same length.'
'Faster'
from itertools import combinations
import os
import sys
import shutil
import math
import distutils.dir_util
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
				shutil.copytree(f, dest_root+"/"+str(i)+"/"+activity_dir+"/"+f)
				
		
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


def genFoldsOpt(fold_num, target_length, traceDict, delta, dest_root):
	lower_bound = target_length - delta
	upper_bound = target_length + delta
	total_set_num = 4

	for activity in traceDict:
		sorted_file_pair = sorted(traceDict[activity], key=lambda x:x['length'], reverse=True)	
		for i in xrange(fold_num):
			print "dealing with activitiy:", getActivity(activity), "folder:", (i+1)
			cur_total_time = 0
			set_counter = 0
			while((cur_total_time < lower_bound) and (len(sorted_file_pair) > 0)):
				# start picking the trace
				ratio = (set_counter % total_set_num)/ (total_set_num * 1.0)
				index = int(math.floor(ratio * len(sorted_file_pair)))
				print 'cur_length', cur_total_time,'ratio', ratio ,'index',index,'possible trace num', len(sorted_file_pair)

				if (sorted_file_pair[index]['length'] + cur_total_time) > upper_bound:
					
					
					closest_dist = target_length

					for pair in sorted_file_pair:
						if abs(pair['length'] + cur_total_time - target_length) < closest_dist:
							closest_dist = abs(pair['length'] + cur_total_time - target_length)
							closest_pair = pair
				
					new_file_name = closest_pair['path'].split("/")[-1]
					activity_dir = getActivity(activity)
					print 'last',dest_root+"/"+str(i+1)+"/"+activity_dir+"/"+new_file_name
					src_path = closest_pair['path']
					dst_path = dest_root+"/"+str(i+1)+"/"+activity_dir+"/"+new_file_name
					distutils.dir_util.copy_tree(src_path,dst_path)

						##
					cur_total_time += closest_pair['length']
					sorted_file_pair.remove(closest_pair)

					
					break
				else:
					
					trace = sorted_file_pair[index]
					
					## copy file
					new_file_name = trace['path'].split("/")[-1]
					activity_dir = getActivity(activity)
					print 'normal',dest_root+"/"+str(i+1)+"/"+activity_dir+"/"+new_file_name
					src_path = trace['path']
					dst_path = dest_root+"/"+str(i+1)+"/"+activity_dir+"/"+new_file_name
					distutils.dir_util.copy_tree(src_path,dst_path)
					
					#shutil.copytree(trace['path'], dest_root+"/"+str(i+1)+"/"+activity_dir+"/"+ new_file_name)
					##
					
					cur_total_time += trace['length']
					set_counter += 1
					sorted_file_pair.remove(trace)
					
			print '++++ total_length:', cur_total_time, '++++'	

if __name__ == "__main__":
	if (len(sys.argv) < 4):
		print "Usage: all-user-dir fold-num dest-folder delta"
		exit(5)


	root = sys.argv[1]
	fold_num = int(sys.argv[2])
	dest_path = sys.argv[3]
	delta = int(sys.argv[4])

	for i in xrange(fold_num):
		folder = str(i+1)
		if not os.path.exists(dest_path+"/"+ folder): 
			os.makedirs(dest_path+"/"+ folder)	
		if not os.path.exists(dest_path+"/"+folder+"/s"):
			os.makedirs(dest_path+"/"+ folder + "/s")	
		if not os.path.exists(dest_path+"/"+folder+"/w"):
			os.makedirs(dest_path+"/"+ folder + "/w")	
		if not os.path.exists(dest_path+"/"+folder+"/b"):
			os.makedirs(dest_path+"/"+ folder + "/b")	
		if not os.path.exists(dest_path+"/"+folder+"/r"):
			os.makedirs(dest_path+"/"+ folder + "/r")	
		if not os.path.exists(dest_path+"/"+folder+"/d"):
			os.makedirs(dest_path+"/"+ folder + "/d")
	traceDict = getTraceLengthDict(root) # a dict(activity) of a list of dict(filename, length)
	
	activity_total_length = compute_activity_total_time(traceDict)
	activity_total_length.sort()
	print activity_total_length
	activity_length_for_each_folder =  activity_total_length[0]/(fold_num * 1.0)
	print "the length of each activity within one folder", activity_length_for_each_folder	
	genFoldsOpt(fold_num, activity_length_for_each_folder, traceDict, delta, dest_path)
	#print activity_total_length	
	
			
	
