#! /bin/bash
if [ $# -lt 6 ]; then
 echo "Usage: train-trace test-trace activity feature file1 activity1 file2 activity2 ..."
 echo "Enter GPS|GSM|Wifi|Accel for feature"
 exit 
fi
train_trace=$1
test_trace=$2
activity=$3
feature=$4

cd ~/cita/Mobility-Detector/evaluation
java extract"$feature"Features $train_trace $activity
mv $feature.out  train.out

cmd_line=($@)                                # extract the command line
other_args=(${cmd_line[@]:4})                # get the variable part of the command line
length=${#other_args[@]}
echo ${other_args[@]}
i=0
echo "Num arg is $length"
while [ $i -lt $length ] ; do
   trace_file=${other_args[$i]}
   trace_activity=${other_args[`expr $i '+' 1`]}
   java extract"$feature"Features  $trace_file $trace_activity
   cat $feature.out >> train.out
   i=`expr $i '+' 2`
done
java extract"$feature"Features $test_trace $activity
mv $feature.out test.out
components=($(head -n1 test.out | tr "," "\n"))
num_components=`expr ${#components[@]} '-' 1`
echo "Number of feature vector Components are "$num_components
matlab -r "classification ('train.out','test.out',$num_components) " -nodesktop
