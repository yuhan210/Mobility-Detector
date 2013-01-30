
fold_num=$1

code_path="/home/dept/ta/yuhan/mobility-detector/src/Mobility-Detector/activity-detection/src"

python ${code_path}/eval-classifier.py ~/mobility-detector/stitched-trace/$fold_num/stitched-trace-123.out ${code_path}/power.py 1-2-3 ~/mobility-detector/kde_classifier/${fold_num}/kernel_classifier_model_${fold_num} ${fold_num}

