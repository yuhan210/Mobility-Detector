import sys
import os
import pickle
if __name__ == "__main__":
	if ( len(sys.argv) < 3):
		print 'Usage:', sys.argv[0], 'path_to_feature fold_num'
		exit(5)
	
	path_to_feature = sys.argv[1]
	fold_num = int(sys.argv[2])

	
	for fold in xrange(1,11):
		mean_stats = {}
		sigma_stats = {}
		pf_stats = {}
		sv_stats = {}
		for i in xrange(5):
			mean_stats[i] = []
			sigma_stats[i] = []
			pf_stats[i] = []
			sv_stats[i] = []

		for fold_ite in xrange(1,11):
			if fold_ite != fold_num:
				path = path_to_feature + '/' + str(fold_ite) + '/' + str(fold_ite) + '_test_accel.arff'

				feature_file = open(path,'r')
				
				for line in feature_file.readlines():
					mean = float(line.split(',')[0])
					sigma = float(line.split(',')[1])
					sv = float(line.split(',')[3])
					pf = float(line.split(',')[4])
					gnd_truth = int(line.split(',')[-1])

					mean_stats[gnd_truth] += [mean]
					sigma_stats[gnd_truth] += [sigma]
					pf_stats[gnd_truth] += [pf]
					sv_stats[gnd_truth] += [sv]
		output_fv_dict = {}
		for i in xrange(5):
			output_fv_dict[i] = []
			output_fv_dict[i] += [mean_stats[i]]
			output_fv_dict[i] += [sigma_stats[i]]
			output_fv_dict[i] += [pf_stats[i]]
			output_fv_dict[i] += [sv_stats[i]]
		
		fh=open('/home/dept/ta/yuhan/mobility-detector/kde_classifier/'+ str(fold) + '/kernel_classifier_model_'+ str(fold), 'w')
		pickle.dump(output_fv_dict,fh)
				
