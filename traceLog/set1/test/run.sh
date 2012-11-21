#! /bin/bash

if [ $# -lt 1 ]; then
 echo "Usage: seed"
 exit
fi


seed=$1
## test

cat ./static/* > static.out
cat ./walking/* > walking.out
cat ./biking/* > biking.out
cat ./running/* > running.out
cat ./driving/* > driving.out


python ~/cita/activity-detection/src/stitch-traces.py 1000000 static.out walking.out running.out biking.out driving.out $seed

./test.sh $seed


