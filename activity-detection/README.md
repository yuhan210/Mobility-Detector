activity-detection
==================

Infrastructure to test different classifiers for mobile phone based activity detection 

-----------
eval-classifier.py is the trace driven simulation. It needs as input all sensor traces over the same time interval

This is how you run it :
python eval-classifier.py ~/cita/CITA_DATA/Tiffany/2012-07-18-18-18-29_driving/Accel2012-07-18-18-18-29_driving ~/cita/CITA_DATA/Tiffany/2012-07-18-18-18-29_driving/Wifi2012-07-18-18-18-29_driving ~/cita/CITA_DATA/Tiffany/2012-07-18-18-18-29_driving/GPS2012-07-18-18-18-29_driving ~/cita/CITA_DATA/Tiffany/2012-07-18-18-18-29_driving/GSM2012-07-18-18-18-29_driving ~/cita/CITA_DATA/Tiffany/2012-07-18-18-18-29_driving/Geo\ Loc2012-07-18-18-18-29_driving

----------
stitch-trace.py allows us to generate arbitrary length traces from a simulated Markov Chain

This is how you run it :

python src/stitch-traces.py 100 ~/cita/CITA_DATA/Tiffany/2012-04-04-16-56-43_static/Accel2012-04-04-16-56-43_still_indoor_static ~/cita/CITA_DATA/Tiffany/2012-04-16-15-32-28_walking/Accel2012-04-16-15-32-28_walking_outdoor_sp_flour ~/cita/CITA_DATA/Chern/2012-10-13-21-09-15_running/Accel2012-10-13-21-09-15_running ~/cita/CITA_DATA/Tiffany/2012-09-24-16-22-36_biking/Accel2012-09-24-16-22-36_biking ~/cita/CITA_DATA/Tiffany/2012-08-03-18-44-22_driving/Accel2012-08-03-18-44-23_driving

-----
train-classifier.py is the training phase for the classifier. It needs as input a reasonable amount of sensor traces from all labels
python train-classifier.py ~/Dropbox/CITA_DATA/Tiffany-Nexus-One/2012-07-18-18-18-29_driving/Accel2012-07-18-18-18-29_driving ~/Dropbox/CITA_DATA/Tiffany-Nexus-One/2012-07-18-18-18-29_driving/Wifi2012-07-18-18-18-29_driving ~/Dropbox/CITA_DATA/Tiffany-Nexus-One/2012-07-18-18-18-29_driving/GPS2012-07-18-18-18-29_driving ~/Dropbox/CITA_DATA/Tiffany-Nexus-One/2012-07-18-18-18-29_driving/GSM2012-07-18-18-18-29_driving ~/Dropbox/CITA_DATA/Tiffany-Nexus-One/2012-07-18-18-18-29_driving/Geo\ Loc2012-07-18-18-18-29_driving
