#! /bin/bash

python ~/cita/activity-detection/src/train-classifier.py accel.out wifi.out gps.out gsm.out nwkloc.out 1> /dev/null 2> classifier.model
