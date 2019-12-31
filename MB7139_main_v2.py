#!/usr/bin/env python
#
# Available device: Ultrasonic sensor
# Manufacturer: MaxBotix Inc.
# Product number: MB7139-100
# Serial communication protocol: Pulse-width measurement by using GPIO
# Purpose:
# Detect water level every 1 hr (Unit in cm)
# 
# Updated:
# 2019/12/28
# 
# Version: 1.1
#

# Including
from statistics import median
import time
import RPi.GPIO as GPIO
import urllib3
from time import gmtime, strftime
#from urllib.request import urlopen
from urllib2 import urlopen
import statistics

# Definition of variable
id_No    = "9999"
samplingList = []
sampNum  = 20
GPIO_TRIGECHO =  15  # Define GPIO to use on RPi
countNum_Loop = -1
officalThreshold = 5.0 # Unit in cm
debug = True
stdMultiple = 5

# Use BCM GPIO references instead of physical pin numbers 
GPIO.setmode(GPIO.BCM)
# Set pins as output and input
GPIO.setup(GPIO_TRIGECHO,GPIO.IN)  # Initial state as input
GPIO.setwarnings(False)

def sampling():
  # This function measures a distance
  # Set line to input to check for start of echo response
    GPIO.setup(GPIO_TRIGECHO, GPIO.IN)
    while GPIO.input(GPIO_TRIGECHO) == 0:
        continue
    start = time.time() # Unit in sec
  # Wait for end of echo response
    while GPIO.input(GPIO_TRIGECHO) == 1:
        continue
    stop = time.time() # Unit in sec

    elapsedOneway = (stop-start)/2.0
    distance = elapsedOneway * (331.4 + 0.606 * 25) * 100 # Unit in cm
    time.sleep(0.1)
    return distance

# def findMedian():
#     countNum = 0
#     samplingList = []
#     while (countNum <= sampNum):
#         samplingList.append(float(sampling()))
#         medianVal = median(samplingList)
#         countNum += 1
#     return medianVal

def find_avg_std():
    countNum = 0
    samplingList = []
    while (countNum <= sampNum):
        samplingList.append(float(sampling()))      
        countNum += 1

    std = statistics.stdev(samplingList)
    mean = statistics.mean(samplingList)

    # not_outlier_num = 0
    # for ii in range(0, len(samplingList)):    
    #     if  (mean - 1 * std < samplingList[ii] < mean + 1 * std):
    #         not_outlier_num += 1

    # not_outlier_ratio = not_outlier_num/len(samplingList)

    # Remove Outliers from  mean +- std
    samplingList = [x for x in samplingList if (x > mean - 1 * std)]
    samplingList = [x for x in samplingList if (x < mean + 1 * std)]

    std_new  = statistics.stdev(samplingList)
    mean_new = statistics.mean(samplingList)
    return [mean_new, std_new]

def debugMod():
    countNum = 0
    sampNum = 10
    samplingList = []
    while (countNum <= sampNum):
        samplingList.append(float(sampling()))      
        countNum += 1

    std = statistics.stdev(samplingList)
    mean = statistics.mean(samplingList)

    print("---------- Result ----------")
    print("Sampling list:")
    print(samplingList)
    print("Mean: {}".format(mean))
    print("StdV: {}".format(std))

    # not_outlier_num = 0
    # for ii in range(0, len(samplingList)):    
    #     if  (mean - 1 * std < samplingList[ii] < mean + 1 * std):
    #         not_outlier_num += 1

    # not_outlier_ratio = not_outlier_num/len(samplingList)

    # Remove Outliers from  mean +- std
    samplingList = [x for x in samplingList if (x > mean - stdMultiple * std)]
    samplingList = [x for x in samplingList if (x < mean + stdMultiple * std)]

    std_new  = statistics.stdev(samplingList)
    mean_new = statistics.mean(samplingList)

    print("---------- Rearranging Result ----------")
    print("Sampling list:")
    print(samplingList)
    print("Mean: {}".format(mean_new))
    print("StdV: {}".format(std_new))
    time.sleep(5)
    

def pipeLg():
    # pLg = 0.0
    # pLg = round(findMedian(),3)
    print("Start to measure the total length of pipeline......")    
    pLg_list = find_avg_std()
    print("Mean: {}".format(pLg_list[0]))
    print("StdV: {}".format(pLg_list[1]))
    print("StdV * {}: {}".format(stdMultiple, pLg_list[1]*5))
    return pLg_list

def waterLev(arg1):
    print("Start measurement......")
    pLg_meas = find_avg_std()
    print("Mean: {}".format(pLg_meas[0]))
    print("StdV: {}".format(pLg_meas[1]))

    if  arg1[0] - stdMultiple * arg1[1] < pLg_meas[0] < arg1[0] + stdMultiple * arg1[1]:
        # avg_pipeLg - 1 * stdvar  < measurement < avg_pipeLg + 1 * stdvar
        wLev = 0.0 # There is no water
    else:
        # water level = pipe length - measurement
        wLev = arg1[0] - pLg_meas[0]

    # while True:
    #     print("Start measurement......")
    #     wLev = round((arg1 - sampling()),3)
    #     if (wLev > settlementDep):
    #         if (settlementDep < wLev < 0.3):
    #             wLev = 0.0 # To reduce the noise from the environment
    #         break
    #     else:
    #         print("Error in detecting the water level.")
    #         print("Send a log information back to the server.")
    #         httpPOST(id_No, wLev, "Error", 0)
    #         countNum_Loop = -1
    return wLev
            
def httpPOST(String0, String1, String2, String3):    
    try:
        global timeStamp
        timeStamp = strftime("%Y%m%d%H%M00")
        #url = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?site=Mucha&time='+repr(timeStamp)+'&weather=0&id='+ str(String0) + \
        #      '&air=0&acceleration=0&cleavage=0&incline=0&field1='+repr(String1)+'&field2='+repr(String2)+'&field3='+repr(String3)
        url  = 'http://ec2-54-175-179-28.compute-1.amazonaws.com/update_general.php?site=FD01_RMO' + \
                '&t=' + repr(timeStamp) + \
                '&id='+ repr(String0) + \
                '&d=' + repr(String1) + \
                '&f1='+ repr(String2) + \
                '&f2='+ repr(String3)  
        resp = urlopen(url).read()
        #hturtpCode = resp.code
        print('------------------------')
    except:
         print('We have an error!')
         print('Waiting for 20 seconds')
         time.sleep(20)
         resp = urlopen(url).read()         
         print('------------------------')
    
def scenarioDetect(arg2):
    if (arg2 > 0.0) & (arg2 < officalThreshold):        
        sleepT = 60*10 # Unit in sec
    elif (arg2 > 0.0) & (arg2 >= officalThreshold):
        sleepT = 60*5 # Unit in sec
    else:        
        sleepT = 60*30 # Unit in sec        
    return sleepT    

if not debug:
    try:
        while True:
            while (countNum_Loop < 0):
                pLgVal  = pipeLg()
                httpPOST(id_No, 0.00, round(pLgVal[0],3), "Reboot")
                countNum_Loop += 1
            
            wLevVal = waterLev(pLgVal)
            if countNum_Loop == -1:
                break
            
            sleepT = scenarioDetect(wLevVal)
            
            print("Upload time : %s" % timeStamp)
            print("Pipe length : %.3f cm" % pLgVal[0])
            print("Water level : %.3f cm" % wLevVal)
            httpPOST(id_No, round(wLevVal,3), 0, 0)        
            time.sleep(sleepT)

    except KeyboardInterrupt:
        print("Stop")
        GPIO.cleanup()
else:
    debugMod()