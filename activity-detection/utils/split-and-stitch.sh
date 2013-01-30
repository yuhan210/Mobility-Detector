#! /bin/bash
# Take a combined indoor-outdoor trace collected using our random walk experiments.
# Write it out piecewise into an indoor and outdoor folder so that stitch-io-traces.py can use it.
# call stitch-io-traces.py to stitch it
# add empty files for other sensors.
if [ $# -ne 3 ] ; then
	echo "Usage : enter name of random walk folder , duration and seed "
	exit
fi;

random_walk_folder=$1
duration=$2
seed=$3
rm -rf unknown_templates indoor_templates outdoor_templates
mkdir unknown_templates indoor_templates outdoor_templates
cat $random_walk_folder/Wifi*  |  python split-io-traces.py
python ../src/stitch-io-traces.py $duration indoor_templates outdoor_templates $seed
touch stitched-GPS.out
touch stitched-GSM.out
touch stitched-Accel.out
touch stitched-GeoLoc.out
