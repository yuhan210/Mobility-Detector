'''
Parse weka prediction outputs and run dhmm on top of the predictions
'''
import sys
from math import *
def parseWekaOutputFile(file_path):
	output_file = open(file_path)
	buf = map(lambda x : x.strip(), output_file.readlines())
	
	header_index = buf.index("inst#,    actual, predicted, error, probability distribution")+1
	tail_index = buf.index("=== Evaluation on test set ===")-1
	contents = buf[header_index:tail_index]
	
	weka_result_list = []
	for string in contents:
		weka_result =  map( lambda x: x if x[0] != '*' else x[1:] , filter( lambda x: x != '' and x != '+', string.split(" ")))
		prediction = {}
		prediction['gnd_truth'] = int(weka_result[1].split(':')[1])
		prediction['prediction'] = int(weka_result[2].split(':')[1])
		prediction['prob_dist'] = map( lambda x : float(x), weka_result[3:])
		weka_result_list.append(prediction)
	
	return weka_result_list

def dhmm(ob_list, transition_prob):
	state_score = [0,0,0,0,0]
	hmm_result_list = []	
	for weka_ob in ob_list:
		new_state_score = [0,0,0,0,0]

		for i in xrange(5):
			max_score = -1.0 * sys.float_info.max
			for j in xrange(5):
				transition_score = transition_prob[j][i]
				cand_score = state_score[j] + log(transition_score) + log(max(weka_ob['prob_dist'][i],0.001))
				if cand_score > max_score:
					max_score = cand_score

			new_state_score[i] = max_score
	
		for i in xrange(5):
			state_score[i] = new_state_score[i]
	
		hmm_pred = {}
		hmm_pred['gnd_truth'] = weka_ob['gnd_truth']
		hmm_pred['prediction'] = state_score.index(max(state_score))
		hmm_pred['prob_dist'] =list(state_score)
		hmm_result_list.append(hmm_pred)

	return hmm_result_list

def getAccuracy(pred_result):
	
	result = {}
	result['accuracy'] = len(filter( lambda x : x['gnd_truth'] == x['prediction'], pred_result))/(len(pred_result)*1.0)
	return result['accuracy']

if __name__ == "__main__":
	if ( len(sys.argv) < 2):
		print "Usage: ", sys.argv[0],"weka_prediction_output"
		exit(5)
	
	weka_output_file = sys.argv[1]

	# a list of dict(gnd_truth, prediction, prob dist:[])
	weka_pred_result = parseWekaOutputFile(weka_output_file)
	# a list of dict(gnd_truth, prediction, prob dist:[])
	transition_prob = [[1,0.2,0.2,0.2,0.2],[0.2,1,0.1,0.2,0.1],[0.2,0.2,1,0.00000001,0.00000001],[0.2,0.00000001,0.00000001,1,0.00000001],[0.2,0.00000001,0.00000001,0.00000001,1]]
	hmm_pred_result = dhmm(weka_pred_result,transition_prob)
	# precision, recall, accuracy
	print getAccuracy(weka_pred_result)
	print getAccuracy(hmm_pred_result)
