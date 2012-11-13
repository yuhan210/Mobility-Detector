#! /bin/bash
# biking driving
echo "--biking,driving--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta"
 ./run-harness.sh ~/cita/CITA_DATA/Anirudh/2012-09-24-19-10-17_biking/ ~/cita/CITA_DATA/Anirudh/2012-09-30-17-52-22_biking/ 3 ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4 Accel $sampling_delta | grep "RESULT"
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--walking,driving--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Anirudh/2012-09-27-09-52-43_walking ~/cita/CITA_DATA/Anirudh/2012-09-26-12-15-36_walking 1 ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--walking,static--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Anirudh/2012-09-27-09-52-43_walking ~/cita/CITA_DATA/Anirudh/2012-09-26-12-15-36_walking 1 ~/cita/CITA_DATA/Chern/2012-10-02-18-29-02_static 0 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--walking,running--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Anirudh/2012-09-27-09-52-43_walking ~/cita/CITA_DATA/Anirudh/2012-09-26-12-15-36_walking 1 ~/cita/CITA_DATA/Chern/2012-10-05-18-23-16_running 2 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--driving,walking--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Tiffany/2012-10-06-06-48-16_driving ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4 ~/cita/CITA_DATA/Anirudh/2012-09-27-09-52-43_walking 1 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--driving,static--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Tiffany/2012-10-06-06-48-16_driving ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4 ~/cita/CITA_DATA/Chern/2012-10-02-18-29-02_static 0 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--driving,running--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Tiffany/2012-10-06-06-48-16_driving ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4 ~/cita/CITA_DATA/Chern/2012-10-12-01-41-07_running 2 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done


echo "--driving,biking--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Tiffany/2012-10-06-06-48-16_driving ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4  ~/cita/CITA_DATA/Chern/2012-09-15-16-37-46_biking 3 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--running,driving--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Chern/2012-10-12-01-41-07_running ~/cita/CITA_DATA/Chern/2012-10-05-18-23-16_running 2 ~/cita/CITA_DATA/Ernie/2012-10-06-12-51-18_driving 4 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--running,biking--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Chern/2012-10-12-01-41-07_running ~/cita/CITA_DATA/Chern/2012-10-05-18-23-16_running 2 ~/cita/CITA_DATA/Chern/2012-09-15-16-37-46_biking 3 Accel $sampling_delta | grep "RESULT"
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--running,static--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Chern/2012-10-12-01-41-07_running ~/cita/CITA_DATA/Chern/2012-10-05-18-23-16_running 2 ~/cita/CITA_DATA/Chern/2012-10-02-18-29-02_static 0 Accel $sampling_delta | grep "RESULT"
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--running,walking--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Chern/2012-10-12-01-41-07_running ~/cita/CITA_DATA/Chern/2012-10-05-18-23-16_running 2 ~/cita/CITA_DATA/Chern/2012-10-04-23-22-18_walking 1 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--biking,static--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
 ./run-harness.sh ~/cita/CITA_DATA/Anirudh/2012-09-24-19-10-17_biking/ ~/cita/CITA_DATA/Anirudh/2012-09-30-17-52-22_biking/ 3 ~/cita/CITA_DATA/Chern/2012-10-02-18-29-02_static 0 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done

echo "--biking,running--"
sampling_rate=1
while [ $sampling_rate -lt 50 ] ; do
  sampling_delta=`echo "scale=5; 1 / $sampling_rate;" | bc `
  cd ~/cita/Mobility-Detector/evaluation;
  echo "Sampling rate is $sampling_rate, Sampling interval is $sampling_delta" 
  ./run-harness.sh ~/cita/CITA_DATA/Anirudh/2012-09-24-19-10-17_biking/ ~/cita/CITA_DATA/Anirudh/2012-09-30-17-52-22_biking/ 3 ~/cita/CITA_DATA/Chern/2012-10-12-01-41-07_running 2 Accel $sampling_delta | grep "RESULT" 
  sampling_rate=`expr $sampling_rate '+' 5`
done
