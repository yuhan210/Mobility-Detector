#! /bin/bash
if [ $# -lt 6 ]; then
 echo "Usage: train-file test-file test_activity negative_train_samples negative_activity feature"
 echo "Enter Gps|Gsm|Wifi|Accel for feature"
 exit 
fi
train_file=$1
test_file=$2
activity=$3
negative_train_samples=$4
negative_activity=$5
feature=$6

java extract"$feature"Features $train_file $activity
mv $feature.out  train.out
java extract"$feature"Features $negative_train_samples $negative_activity
cat $feature.out >> train.out
java extract"$feature"Features $test_file $activity
mv $feature.out test.out
matlab -r "classification ('train.out','test.out') " -nodesktop
