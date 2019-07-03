#!/usr/bin/env python
#
# Available device: Ultrasonic sensor
# Manufacturer: MaxBotix Inc.
# Product number: MB7139-100
# Serial communication protocol: Pulse-width measurement by using GPIO
# Purpose:
# Detect water level every 1 hr (Unit in cm)
# 
#

# Including
from statistics import median
import time
import RPi.GPIO as GPIO
import urllib3
from time import gmtime, strftime
from urllib.request import urlopen

# Definition of variable
id_No    = "9999"
samplingList = []
sampNum  = 20
settlementDep = -1.0 # Unit in cm
GPIO_TRIGECHO =  15  # Define GPIO to use on RPi
countNum = -1
officalThreshold = 5.0 # Unit in cm

# Use BCM GPIO references instead of physical pin numbers 
GPIO.setmode(GPIO.BCM)
# Set pins as output and input
GPIO.setup(GPIO_TRIGECHO,GPIO.OUT)  # Initial state as output
# Set trigger to False (Low)
GPIO.output(GPIO_TRIGECHO, False)

def sampling():
  # This function measures a distance
  # Pulse the trigger/echo line to initiate a measurement
    GPIO.output(GPIO_TRIGECHO, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGECHO, False)
  # Ensure start time is set in case of very quick return
    start = time.time()

  # Set line to input to check for start of echo response
    GPIO.setup(GPIO_TRIGECHO, GPIO.IN)
    while GPIO.input(GPIO_TRIGECHO)==0:
        start = time.time() # Unit in sec

  # Wait for end of echo response
    while GPIO.input(GPIO_TRIGECHO)==1:
        stop = time.time() # Unit in sec
  
    GPIO.setup(GPIO_TRIGECHO, GPIO.OUT)
    GPIO.output(GPIO_TRIGECHO, False)

    elapsedOneway = (stop-start)/2.0
    distance = elapsedOneway * (331.4 + 0.606 * 25) * 100 # Unit in cm
    time.sleep(0.1)
    return distance

def findMedian():
    countNum = 0
    while (countNum <= sampNum):
        samplingList.append(float(sampling()))
        medianVal = median(samplingList)
        countNum += 1
    return medianVal

def pipeLg():
    pLg = 0.0
    print("Start to measure the total length of pipeline......")
    pLg = round(findMedian(),3)
    return pLg

def waterLev(arg1):
    while True:
        print("Start measurement......")
        wLev = round((arg1 - sampling()),3)
        if (wLev > settlementDep):
            if (settlementDep < wLev < 0.3):
                wLev = 0.0 # To reduce the noise from the environment
            break
        else:
            print("Error in detecting the water level.")
            print("Send a log information back to the server.")
            httpPOST(id_No, 0, "Error", 0)
    return wLev
            
def httpPOST(String0, String1, String2, String3):
    timeStamp = strftime("%Y%m%d%H%M%S")
    url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?site=Mucha&time='+repr(timeStamp)+'&weather=0&id='+ str(String0) + \
          '&air=0&acceleration=0&cleavage=0&incline=0&field1='+repr(String1)+'&field2='+repr(String2)+'&field3='+repr(String3)
    resp = urlopen(url).read()    
    print('------------------------')
    
def scenarioDetect(arg2):
    if (arg2 > 0.0) & (arg2 < officalThreshold):        
        sleepT = 30 # Unit in sec
    elif (arg2 > 0.0) & (arg2 >= officalThreshold):
        sleepT = 10 # Unit in sec
    else:        
        sleepT = 60 # Unit in sec        
    return sleepT
    

try:
    while True:
        while (countNum < 0):
            pLgVal  = pipeLg()
            httpPOST(id_No, pLgVal, "Reboot", 0)
            countNum += 1
        
        wLevVal = waterLev(pLgVal)              
        print("Pipe length : %.3f cm" % pLgVal)
        print("Water level : %.3f cm" % wLevVal)
        httpPOST(id_No, wLevVal, 0, 0)
        
        time.sleep(30)

except KeyboardInterrupt:
    print("Stop")
    GPIO.cleanup()
