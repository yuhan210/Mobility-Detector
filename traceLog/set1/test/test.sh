#! /bin/bash

if [ $# -lt 1 ]; then
 echo "Usage: seed"
 exit
fi

seed=$1
mkdir ./seeds/$seed


## sampling rate 1 - 9
sampling_rate=1
while [ $sampling_rate -lt 10 ]; do
 sampling_interval=`echo "scale=5; (1 / $sampling_rate) * 1000;" | bc`
 echo "Sampling rate is $sampling_rate, sampling interval is $sampling_interval"

 python ~/cita/activity-detection/src/eval-classifier.py stitched-Accel.out stitched-Wifi.out stitched-GPS.out stitched-GSM.out stitched-Geo\ Loc.out ~/cita/activity-detection/src/power.py ../train/classifier.model $sampling_interval 1> ./seeds/${seed}/${sampling_rate}_stdout.out 2> ./seeds/${seed}/${sampling_rate}_stderr.out
 mv gnd.plot ./seeds/${seed}/${sampling_rate}_gnd.plot
 mv classifier.plot ./seeds/${seed}/${sampling_rate}_classifier.plot

 sampling_rate=`expr $sampling_rate '+' 1`
done


#sampling_rate 10 - 100
sampling_rate=10

while [ $sampling_rate -lt 110 ] ; do
 sampling_interval=`echo "scale=5; (1 / $sampling_rate) * 1000;" | bc`
 echo "Sampling rate is $sampling_rate, sampling interval is $sampling_interval"
 python ~/cita/activity-detection/src/eval-classifier.py stitched-Accel.out stitched-Wifi.out stitched-GPS.out stitched-GSM.out stitched-Geo\ Loc.out ~/cita/activity-detection/src/power.py ../train/classifier.model $sampling_interval 1> ./seeds/${seed}/${sampling_rate}_stdout.out 2> ./seeds/${seed}/${sampling_rate}_stderr.out
 mv gnd.plot ./seeds/${seed}/${sampling_rate}_gnd.plot
 mv classifier.plot ./seeds/${seed}/${sampling_rate}_classifier.plot
 sampling_rate=`expr $sampling_rate '+' 10`
done

