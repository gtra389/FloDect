#!/bin/bash


if [ `ps -U root -u root u | grep python | wc -m` -eq 0 ]
 then 
   sudo python /home/pi/FloDect/MB7139_main_v2.py
   sleep 180
 else
   sleep 180
fi

