#!/bin/bash


folds=(1 2 3 4 5 6 7 8 9 10)
data_path="/home/dept/ta/yuhan/mobility-detector/10-fold"
dest_root="/home/dept/ta/yuhan/mobility-detector/10-fold/feature-data"
for fold_num in "${folds[@]}"
do
	echo $fold_num
	python ./gen-features.py $data_path $fold_num $dest_root/$fold_num/${fold_num}_feature_filtered.arff

done