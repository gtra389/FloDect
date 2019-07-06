#!/bin/bash

sleep 15

sudo python3 /home/pi/3meters/3m_main.py >> log
while :
do
  if [ `ps -U root -u root u | grep python3 | wc -m` -eq 0 ]
  then 
    sudo python3 /home/pi/3meters/3m_main.py >> log
    sleep 180
  else
  	sleep 180
  fi
done
