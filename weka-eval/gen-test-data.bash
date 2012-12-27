#!/bin/bash

if [ $# -lt 1 ]; then
	echo "Enter the folder that is left"
	exit
fi

leave_fold_num=$1 ##train on other folds
data_root="/home/dept/ta/yuhan/mobility-detector/10-fold/feature-data"
array=( "s" "w" "r" "b" "d" )
folds=( 1 2 3 4 5 6 7 8 9 10)
str=""

for fold_num in "${folds[@]}"
do
	if [[ $fold_num -ne $leave_fold_num ]]
	then
		str+=" ${data_root}""/"${fold_num}"/"${fold_num}_feature_filtered.arff

	fi
done
#echo $str
cat $str > $data_root/$leave_fold_num/${leave_fold_num}_train_filtered.arff
#cat $accel > $dest_path/test_accel.out
#cat $gps > $dest_path/test_gps.out
#cat $wifi > $dest_path/wifi.out
#cat $gsm > $dest_path/gsm.out
#touch $dest_path/test_wifi.out
#touch $dest_path/test_gsm.out
#touch $dest_path/test_nwkloc.out
#echo $nwkloc
