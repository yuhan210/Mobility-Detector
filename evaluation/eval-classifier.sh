#! /bin/bash
if [ $# -lt 5 ]; then
 echo "Usage: train-file test-file test_activity negative_train_samples negative_activity"
 exit 
fi
train_file=$1
test_file=$2
activity=$3
negative_train_samples=$4
negative_activity=$5
java extractAccelFeatures $train_file $activity
mv accel.out  train.out
java extractAccelFeatures $negative_train_samples $negative_activity
cat accel.out >> train.out
java extractAccelFeatures $test_file $activity
mv accel.out test.out
matlab -r "classification ('train.out','test.out') " -nodesktop
