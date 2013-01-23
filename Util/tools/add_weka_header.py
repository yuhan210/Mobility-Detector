import sys
import os

if __name__ == "__main__":

	if (len(sys.argv) < 2):
		print 'Usage: ', sys.argv[0],'path_to_folder'

	folder_path = sys.argv[1]
	sensor_feature_list = os.listdir(folder_path)
	for sensor_feature in sensor_feature_list:
		print folder_path+'/'+sensor_feature
		if sensor_feature.find('accel') >= 0:
			
			f = open(folder_path+'/'+sensor_feature,'r')
			tt = open('tmp','w')
			tt.write('@RELATION mode\n\n')
			tt.write('@ATTRIBUTE var NUMERIC\n')
			tt.write('@ATTRIBUTE sv NUMERIC\n')
			tt.write('@ATTRIBUTE pf NUMERIC\n')
			tt.write('@ATTRIBUTE 1hz NUMERIC\n')
			tt.write('@ATTRIBUTE 2hz NUMERIC\n')
			tt.write('@ATTRIBUTE 3hz NUMERIC\n')
			tt.write('@ATTRIBUTE gnd_truth {0,1,2,3,4}\n')
			tt.write('\n@DATA\n')
			tt.write(f.read())
			tt.close()
			f.close()
			os.rename('tmp',folder_path+'/'+sensor_feature)
			
		elif sensor_feature.find('gps') >= 0:
		
			f = open(folder_path+'/'+sensor_feature,'r')
			tt = open('tmp','w')
			tt.write('@RELATION mode\n\n')
			tt.write('@ATTRIBUTE speed NUMERIC\n')
			tt.write('@ATTRIBUTE gnd_truth {0,1,2,3,4}\n')
			tt.write('\n@DATA\n')
			tt.write(f.read())
			tt.close()
			f.close()
			os.rename('tmp',folder_path+'/'+sensor_feature)

		elif sensor_feature.find('wifi') >= 0:
			
			f = open(folder_path+'/'+sensor_feature,'r')
			tt = open('tmp','w')
			tt.write('@RELATION mode\n\n')
			tt.write('@ATTRIBUTE common_ap_ratio NUMERIC\n')
			tt.write('@ATTRIBUTE rssi_dist NUMERIC\n')
			tt.write('@ATTRIBUTE tanimoto NUMERIC\n')
			tt.write('@ATTRIBUTE gnd_truth {0,1,2,3,4}\n')
			tt.write('\n@DATA\n')
			tt.write(f.read())
			tt.close()
			f.close()
			os.rename('tmp',folder_path+'/'+sensor_feature)

		elif sensor_feature.find('gsm') >= 0:

			f = open(folder_path+'/'+sensor_feature,'r')
			tt = open('tmp','w')
			tt.write('@RELATION mode\n\n')
			tt.write('@ATTRIBUTE common_cell_ratio NUMERIC\n')
			tt.write('@ATTRIBUTE rssi_dist NUMERIC\n')
			tt.write('@ATTRIBUTE tanimoto NUMERIC\n')
			tt.write('@ATTRIBUTE gnd_truth {0,1,2,3,4}\n')
			tt.write('\n@DATA\n')
			tt.write(f.read())
			tt.close()
			f.close()
			os.rename('tmp',folder_path+'/'+sensor_feature)

