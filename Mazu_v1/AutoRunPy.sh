#!/bin/bash

sleep 15
sudo python /home/pi/FloDect/MB7139.py >> log
while :
do
  if [ `ps -U root -u root u | grep python | wc -m` -eq 0 ]
  then 
    sudo python /home/pi/FloDect/MB7139.py >> log
    sleep 180
  else
    sleep 180
  fi
done
