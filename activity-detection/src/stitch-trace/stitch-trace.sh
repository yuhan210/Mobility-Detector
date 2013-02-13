#! /bin/bash

seed_num=$1
phone_model=$2

folds=( "1" "2" "3" "4")

rm -rf /home/dept/ta/yuhan/stitched-traces/${phone_model}
mkdir /home/dept/ta/yuhan/stitched-traces/${phone_model}
for fold_num in "${folds[@]}"
do

	path="/home/dept/ta/yuhan/sensor-merged-4-fold/${phone_model}/${fold_num}"
	dst_path="/home/dept/ta/yuhan/stitched-traces/${phone_model}/${fold_num}"
	rm -rf ${dst_path}
	mkdir ${dst_path}

	echo ${path}
	python ~/mobility-detector/src/Mobility-Detector/activity-detection/src/stitch-trace/stitch-traces.py 10800000 ${path}/s ${path}/w ${path}/r ${path}/b ${path}/d ${seed_num}
	mv stitched-trace.out ${dst_path}/stitched-trace-${seed_num}.out

done

