#! /bin/bash
# run IO Detector experiments
i=0
# train Galaxy Nexus Model
cd ~/cita/activity-detection/src
python train-classifier.py ~/cita/io-detector/IO-Data/io-data-Dec3/Accel-dummy ~/cita/io-detector/IO-Data/io-data-Dec3/Wifi-Lenin ~/cita/io-detector/IO-Data/io-data-Dec3/GPS-dummy ~/cita/io-detector/IO-Data/io-data-Dec3/GSM-Lenin ~/cita/io-detector/IO-Data/io-data-Dec3/NwkLoc-dummy ../hardware-model/galaxy/power.py 2> galaxy.model
# run 10 iterations
while [ $i -lt 10 ] ; do
	cd ~/cita/activity-detection/utils
	echo "seed $i"
	./split-and-stitch.sh ~/cita/io-detector/IO-Data/io-data-Dec6/GalaxyNexus/ 10800000 $i	> /dev/null
	cd ~/cita/activity-detection/src
	time python eval-classifier.py ../utils/stitched-Accel.out ../utils/stitched-Wifi.out ../utils/stitched-GPS.out ../utils/stitched-GSM.out ../utils/stitched-GeoLoc.out ../hardware-model/galaxy/power.py galaxy.model 1 > /dev/null
	time python eval-classifier.py ../utils/stitched-Accel.out ../utils/stitched-Wifi.out ../utils/stitched-GPS.out ../utils/stitched-GSM.out ../utils/stitched-GeoLoc.out ../hardware-model/galaxy/power.py galaxy.model 2 > /dev/null
	time python eval-classifier.py ../utils/stitched-Accel.out ../utils/stitched-Wifi.out ../utils/stitched-GPS.out ../utils/stitched-GSM.out ../utils/stitched-GeoLoc.out ../hardware-model/galaxy/power.py galaxy.model both > /dev/null
	i=`expr $i '+' 1`
done
