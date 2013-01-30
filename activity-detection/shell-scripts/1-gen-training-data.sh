#!/bin/bash

##!!! give input, modify data_root!!!

if [ $# -lt 2 ]; then
	echo "Enter the phone model, number of fold that is being trained"
	exit
fi

phone_model=$1
trainSet_num=$2 ##train on other folds

data_root="/data/scratch/ada/"${phone_model}"/data/fold"${trainSet_num}
array=( "s" "w" "r" "b" "d" ) 
accel=""
gsm=""
wifi=""
gps=""
nwkloc=""

for activity in "${array[@]}"
do
	folder_path=${data_root}"/"${activity}

	for trace in ${folder_path}/*
	do
		for file in ${trace}/*
		do
			if [[ `echo "$file" | grep "Accel"` != "" ]]
			then
				accel+=" ${file}"
			fi
			if [[ `echo "$file" | grep "GSM"` != "" ]]
			then
				gsm+=" ${file}"
			fi
			if [[ `echo "$file" | grep "Wifi"` != "" ]]
			then
				wifi+=" ${file}"
			fi
			if [[ `echo "$file" | grep "GPS"` != "" ]]
			then
				gps+=" ${file}"
			fi
			if [[ `echo "$file" | grep "Geo"` != "" ]]
			then
				tmp=$(echo "$file" | sed 's/ /\\  /g')
				nwkloc+=" ${tmp}"
			fi
		done
	done

done
cat $accel > accel.out
cat $gps > gps.out
cat $wifi > wifi.out
cat $gsm > gsm.out
echo $nwkloc
