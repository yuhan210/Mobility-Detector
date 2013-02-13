#!/bin/bash

phone_models=("galaxy" "desire" "vivid" "nexus" "sensation-1" "sensation-2")
folds=(1 2 3 4)

for phone_model in "${phone_models[@]}"
do
	data_path="/home/dept/ta/yuhan/data/"${phone_model}
	dest_root="/home/dept/ta/yuhan/feature/"${phone_model}
	for fold_num in "${folds[@]}"
	do
		echo $fold_num
		python ./ucla-gen-features.py $data_path $fold_num $dest_root/$fold_num/${fold_num}_ucla.arff
	done
done
