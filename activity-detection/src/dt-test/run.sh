
#fold_num=$1
#seed_num=$2
#cp ~/mobility-detector/4-fold-feature-classifier/ucla-classifier/${fold_num}_classifier.py ~/mobility-detector/src/Mobility-Detector/activity-detection/src/dt-test/decisionTree.py
python eval-classifier.py ~/stitched-traces/galaxy/1/stitched-trace-123.out ../../hardware_model/galaxy/power.py 0-1-2-3-4 1
