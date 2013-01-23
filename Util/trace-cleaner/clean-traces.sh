#! /bin/bash

if [ $# -lt 2 ]; then
 echo "Usage: user-trace-folder new-folder-for-clean-trace"
 exit
fi

trace_folder=$1
dest_folder=$2

for x in "$1"* 
do
 echo " "
 echo "$x"
 python traceSanitizer_cutter.py "$x" "$dest_folder"


done
