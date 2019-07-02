#!/usr/bin/env python
#
# Available device: Ultrasonic sensor
# Manufacturer: MaxBotix Inc.
# Product number: MB7139-100
# Serial communication protocol: Pulse-width measurement by using GPIO
# Purpose:
# Detect water level every 1 hr (Unit in cm)
# 


from statistics import median
import time
import RPi.GPIO as GPIO
import urllib3
from time import gmtime, strftime
from urllib.request import urlopen

# Definition of variable
id_No    = "9999"
sampNum  = 8
settlementDep = -1.0 # Unit in cm
GPIO_TRIGECHO =  15  # Define GPIO to use on RPi
countNum2 = -1

# Use BCM GPIO references
# instead of physical pin numbers
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
    countNum1 = 0
    samplingList = []
    while (countNum1 <= sampNum):
        samplingList.append(float(sampling()))
        medianVal = median(samplingList)
        print("Count Number = ", countNum1)
        countNum1 += 1
    return medianVal

def pipeLg():
    pLg = 0.0
    print("Start to measure the total length of pipeline......")
    pLg = findMedian()
    return pLg

def waterLev(arg1):
    while True:
        print("Start measurement......")
        wLev = arg1 - findMedian()
        if (wLev > settlementDep):
            break
        else:
            print("Error in detecting the water level.")
            print("Send a log information back to the server.")
            httpPOST(id_No, 0, "Error", 0)
    return wLev
            
def httpPOST(String0, String1, String2, String3):
    timeStamp = strftime("%Y%m%d%H%M%S")
    url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?site=Mucha&time='+str(timeStamp)+'&weather=0&id='+ str(String0) + \
          '&air=0&acceleration=0&cleavage=0&incline=0&field1='+str(String1)+'&field2='+str(String2)+'&field3='+str(String3)
    resp = urlopen(url).read()
    print(resp)
    print('------------------------')
    

try:
    while True:
        while (countNum2 < 0):
            pLgVal  = pipeLg()
            httpPOST(id_No, pLgVal, "Reboot", 0)
            countNum2 +=1
        
        wLevVal = waterLev(pLgVal)              
        print("Pipe length : %.2f cm" % pLgVal)
        print("Water level : %.2f cm" % wLevVal)
        httpPOST(id_No, wLevVal, 0, 0)
        
        time.sleep(30)

except KeyboardInterrupt:
    print("Stop")
    GPIO.cleanup()
