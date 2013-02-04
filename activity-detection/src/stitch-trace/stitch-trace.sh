#! /bin/bash

fold_num=$1
seed_num=$2
python ~/mobility-detector/src/Mobility-Detector/activity-detection/src/stitch-trace/stitch-traces.py 30000000 ~/mobility-detector/sensor-merged-4-fold/${fold_num}/s ~/mobility-detector/sensor-merged-4-fold/${fold_num}/w ~/mobility-detector/sensor-merged-4-fold/${fold_num}/r ~/mobility-detector/sensor-merged-4-fold/${fold_num}/b ~/mobility-detector/sensor-merged-4-fold/${fold_num}/d ${seed_num}

mv stitched-trace.out stitched-trace-${seed_num}.out

