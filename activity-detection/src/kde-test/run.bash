
phone_models=("galaxy" "nexus" "vivid" "sensation-1" "sensation-2" "desire")
call_backs=("0" "1" "2" "3" "4" "0-1" "0-2" "0-3" "0-4" "1-2" "1-3" "1-4" "2-3" "2-4" "3-4" "0-1-2" "0-1-3" "0-1-4" "0-2-3" "0-2-4" "0-3-4" "1-2-3" "1-2-4" "1-3-4" "2-3-4" "0-1-2-3-4")


for phone_model in "${phone_models[@]}"
do
	for callback in "${call_backs[@]}"
	do
		echo ${phone_model}
		echo ${callback}
		python eval-classifier.py ~/stitched-traces/${phone_model}/1/stitched-trace-123.out ../../hardware-model/${phone_model}/power.py ${callback} ~/cross-user-feature/kde_feature/1_accel.pickle ~/cross-user-feature/kde_feature/1_gsm.arff ~/cross-user-feature/kde_feature/1_wifi.arff ~/cross-user-feature/kde_feature/1_gps.arff 1
		mv *.plot ~/result/${phone_model}/kde/
		mv *.out ~/result/${phone_model}/kde/
	done
done
