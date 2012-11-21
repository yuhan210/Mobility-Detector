#! /bin/bash


array=("static" "walking" "running" "biking" "driving")
accel=""
gsm=""
wifi=""
gps=""
nwkloc=""
for trace in "${array[@]}"
do
	for file in $(ls ${trace}/*)
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
		
	done
done
cat $accel > accel.out
cat $gps > gps.out
cat $wifi > wifi.out
cat $gsm > gsm.out
