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
echo "mean"
matlab -r "classification1 ('train.out','test.out',$num_components) " -nodesktop
echo "var"
matlab -r "classification2 ('train.out','test.out',$num_components) " -nodesktop
echo "pf"
matlab -r "classification3 ('train.out','test.out',$num_components) " -nodesktop
echo "pr"
matlab -r "classification4 ('train.out','test.out',$num_components) " -nodesktop
echo "cl"
matlab -r "classification5 ('train.out','test.out',$num_components) " -nodesktop
echo "nle"
matlab -r "classification6 ('train.out','test.out',$num_components) " -nodesktop
echo "sv"
matlab -r "classification7 ('train.out','test.out',$num_components) " -nodesktop
echo "entropy"
matlab -r "classification8 ('train.out','test.out',$num_components) " -nodesktop
