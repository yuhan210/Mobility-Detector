import sys

def write_header():
	print 'class DecisionTree(object):\n'
	print '\tfv = {}\n'
	print '\tdef __init__(self,fv):'
	print '\t\tself.fv = fv\n'
	print '\t\tself.classify()'
	print '\tdef classify(self):'

if __name__ == "__main__":
	if ( len(sys.argv) < 2):
		print "Usage:", sys.argv[0],'classifier_output_from_weka'
		exit(5)
	feature_dict = {0:'speed', 1:'var',2:'1hz', 3:'2hz', 4:'3hz'}	

	write_header()
	classifier_fhandle = open(sys.argv[1],'r')
	
	
	content = classifier_fhandle.readlines()
	condition_list = []
	for i in xrange(len(content)):
		if content[i].find('public static double classify') >= 0:
			first_function_index = i
		if content[i].find('static double N') >= 0:
			condition_list.append(i)

	first_function = content[first_function_index+4].split('.')[1].split('(')[0]
	print '\t\t p = self.'+ first_function+ '()'
	print '\t\t return p'

	for index in condition_list: # for each condition
		print '\n\tdef '+ content[index].split(' ')[4].split('(')[0]+'(self):\n'
		default_label = content[index+3].strip().split(' ')[2].split(';')[0]
		print '\t\tp = '+ default_label
		feature_num =  content[index+4].split('[')[1].split(']')[0]
		threshold = content[index+4].split('=')[1].split(' ')[1].split(')')[0]

		print '\t\tif self.fv[\''+feature_dict[int(feature_num)]+'\'] <= ' + threshold+ ':'
	
		if content[index+5].find('yuhan.') >= 0: # call another function
			function_name = content[index+5].split('.')[1].split('(')[0]
			print '\t\t\tp = self.'+ function_name + '()'
		else: # return label
			predicted_label = content[index+5].split('=')[1].split(' ')[1].split(';')[0]
			print '\t\t\tp = '+ predicted_label

		print '\t\telif self.fv[\'' + feature_dict[int(feature_num)] + '\'] > ' + threshold + ':'
		
		if content[index+7].find('yuhan.') >= 0: # call another function
			function_name = content[index+7].split('.')[1].split('(')[0]
			print '\t\t\tp = self.'+ function_name + '()'
		else: # return label
			predicted_label = content[index+7].split('=')[1].split(' ')[1].split(';')[0]
			print '\t\t\tp = '+ predicted_label
		print '\t\treturn p'

