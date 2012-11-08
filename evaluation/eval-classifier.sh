#! /bin/bash
if [ $# -lt 6 ]; then
 echo "Usage: train-folder test-folder test_activity negative_train_folder negative_activity feature"
 echo "Enter GPS|GSM|Wifi|Accel for feature"
 exit 
fi
train_trace=$1
test_trace=$2
activity=$3
negative_trace=$4
negative_activity=$5
feature=$6

java extract"$feature"Features $train_trace $activity
mv $feature.out  train.out
java extract"$feature"Features $negative_trace $negative_activity
cat $feature.out >> train.out
java extract"$feature"Features $test_trace $activity
mv $feature.out test.out
components=($(head -n1 test.out | tr "," "\n"))
num_components=`expr ${#components[@]} '-' 1`
echo "Number of feature vector Components are "$num_components
matlab -r "classification ('train.out','test.out',$num_components) " -nodesktop
