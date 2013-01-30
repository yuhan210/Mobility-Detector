#! /bin/bash

if [ $# -lt 2 ]; then
	echo "Enter phone model, the fold number for training"
	exit
fi

phone_model=$1
train_fold_num=$2
rm -rf s
rm -rf w
rm -rf r
rm -rf b
rm -rf d
mkdir s
mkdir w
mkdir r
mkdir b
mkdir d

folds=( "1" "2" "3" "4" )

array=("s" "w" "r" "b" "d")

s_count=0
w_count=0
b_count=0
r_count=0
d_count=0
for fold_num in "${folds[@]}"
do
	if [[ `echo "$fold_num" | grep "$train_fold_num"` == "" ]]
	then
		#not the training fold
		testdata_path="/data/scratch/ada/"${phone_model}"/data/fold${fold_num}"

		#folder_path="${testdata_path}"
		for activity in ${array[@]} 
		do
			for trace in ${testdata_path}"/"${activity}/*
			do
				echo ${trace}
				if [[ `echo "$activity" | grep "s"` != "" ]]
				then
					cat ${trace}/* > s/${activity}-${s_count}
					s_count=$(( s_count+1 ))
				fi
				if [[ `echo "$activity" | grep "w"` != "" ]]
				then
					cat ${trace}/* > w/${activity}-${w_count}
					w_count=$(( w_count+1 ))
				fi
				if [[ `echo "$activity" | grep "r"` != "" ]]
				then
					cat ${trace}/* > r/${activity}-${r_count}
					r_count=$(( r_count+1 ))
				fi
				if [[ `echo "$activity" | grep "b"` != "" ]]
				then
					cat ${trace}/* > b/${activity}-${b_count}
					b_count=$(( b_count+1 ))
				fi
				if [[ `echo "$activity" | grep "d"` != "" ]]
				then
					cat ${trace}/* > d/${activity}-${d_count}
					d_count=$(( d_count+1 ))
				fi

			done

		done

	fi
done

