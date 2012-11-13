#! /bin/bash
# cmdline argument handling 
if [ $# -lt 5 ]; then
 echo "Usage: train-folder test-folder feature sampling_interval folder1 folder2 ... ... ... " 
 echo "Enter GPS|GSM|Wifi|Accel for feature"
 exit 
fi

# gets activity number from activity name 
function get_activity {
    name_of_activity=$1
    if [ $name_of_activity = "static" ] ; then
      echo 0
    elif [ $name_of_activity = "walking" ] ; then
      echo 1
    elif [ $name_of_activity = "running" ] ; then
      echo 2
    elif [ $name_of_activity = "biking" ] ; then
      echo 3
    elif [ $name_of_activity = "driving" ] ; then
      echo 4
    else 
      echo "Invalid activity"
      exit;
    fi;
}

# fixed parameters 
train_folder=$1
test_folder=$2
feature=$3
sampling_interval=$4

# get last field in a file name, to get activity name. Must ensure there are no trailing /'s
recs=($(echo $train_folder | tr "/" "\n")) 
length=${#recs[@]}
activity_name=$(echo $train_folder | cut -f `expr $length '+' 1`  -d '/' | cut -f 2 -d '_' )
activity=$(get_activity $activity_name)
# TODO: Ensure activity is the same whether extracted from $train_folder or $test_folder

# get trace file names
train_trace=$(ls $train_folder/"$feature"*)
test_trace=$(ls $test_folder/"$feature"*)

# downsample train and test files
python ~/cita/Mobility-Detector/evaluation/downsample.py $train_trace $sampling_interval > /tmp/train.sampled
python ~/cita/Mobility-Detector/evaluation/downsample.py $test_trace $sampling_interval  > /tmp/test.sampled

# variable parameters
cmd_line=($@)                              # extract the command line
other_folders=(${cmd_line[@]:4})             # get the variable part of the command line
for x in ${other_folders[@]} ; do               # for each folder
   trace_name=$(ls $x/"$feature"*)         # get trace name
   other_traces=("${other_traces[@]}" "$trace_name" )                                       # append trace to other_traces array        

   other_activity_name=$(echo $x | cut -f `expr $length '+' 1` -d '/' | cut -f 2 -d '_' )   # get other activity name
   other_activity=$(get_activity $other_activity_name)                                      # get activity code number
   other_activities=("${other_activities[@]}" "$other_activity" )                           # append activity code to other_activities array
done

# downsample uniformly across all other traces
length=${#other_traces[@]}
i=0
while [ $i -lt $length ] ; do
   python ~/cita/Mobility-Detector/evaluation/downsample.py ${other_traces[$i]} $sampling_interval > /tmp/${other_activities[$i]}.sampled 
   vararg=("${vararg[@]}" "/tmp/${other_activities[$i]}.sampled") # append to other_sampled_traces array
   vararg=("${vararg[@]}" "${other_activities[$i]}")
   i=`expr $i '+' 1`
done

echo "./eval-multi-label-classifier.sh /tmp/train.sampled /tmp/test.sampled $activity $feature ${vararg[@]}"
./eval-multi-label-classifier.sh /tmp/train.sampled /tmp/test.sampled $activity $feature ${vararg[@]}
