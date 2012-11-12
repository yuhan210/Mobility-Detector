#! /bin/bash
if [ $# -lt 7 ]; then
 echo "Usage: train-folder test-folder test_activity negative_train_folder negative_activity feature sampling_interval"
 echo "Enter GPS|GSM|Wifi|Accel for feature"
 exit 
fi
train_folder=$1
test_folder=$2
activity=$3
negative_folder=$4
negative_activity=$5
feature=$6
sampling_interval=$7
train_trace=$(ls $train_folder/"$feature"*)
test_trace=$(ls $test_folder/"$feature"*)
negative_trace=$(ls $negative_folder/"$feature"*)
python ../downsample.py $train_trace $sampling_interval > train.sampled
python ../downsample.py $test_trace $sampling_interval  > test.sampled
python ../downsample.py $negative_trace $sampling_interval > negative.sampled 
./eval-classifier.sh train.sampled test.sampled $activity negative.sampled $negative_activity $feature
