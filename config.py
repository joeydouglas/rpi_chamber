#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import sys
import Adafruit_DHT
from Adafruit_SHT31 import *

#---------
#Variables
#---------
#Database IP
dbIP = "192.168.1.30"
#Influxdb port. Default is 8086.
dbPort = "8086"
#Influxdb database name
dbName = "meatsack"
#Name of the curing chamber. Mostly useful if you have more than one.
chamberName = "meatsack"
#Desired temp/humidity set here.
desiredTemperature = 15.5
desiredHumidity = 80
#Set the drift or fluctuation allowed before outputs are changed to adjust the temp/humidity.
driftTemperature = 1
driftHumidity = 1
#How long should the program sleep in between sensor readings?
sensorSleep = 5
#How long must the fridge be on/off for? This prevents the fridge from cycling on/off every few seconds.
fridgeCycle = 30
#Turn humidifier on and stall the fridge from turning on for a number of seconds to lessen the impact on the humidity.
fridgeStall = 20

#Set timestamp in seconds. Only change if you need time accuracy beyond seconds.
seconds = int(time.time())

#Set GPIO pin specification. DO NOT CHANGE!
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#----------------------------
#Setup temp/humidity sensors.
#----------------------------
#Supported sensors. DO NOT CHANGE!
DHT11  = 11
DHT22  = 22
AM2302 = 22
SHT31_1 = SHT31(address = 0x44)
SHT31_2 = SHT31(address = 0x45)

#Setup variable for a sensor list. DO NOT CHANGE!
allSensors = [[]]

#Installed sensors. This will vary depending on your setup. Only one internal
#temp/humidity sensor (sensor1Internal) is required. 
#Sensor 1 - Primary sensor - will determine which devices are turned on/off.
#--------
sensor1Internal = SHT31_1
sensor1InternalPin = "i2c"
allSensors[0] = [sensor1Internal, sensor1InternalPin, "internal", "sensor1"]
#Sensor 2 - Optional additional sensor.
#--------
#sensor2Internal = AM2302
#sensor2InternalPin = 22
#allSensors.insert(1, [sensor2Internal, sensor2InternalPin, "internal", "sensor2"])
#Sensor 3 - Optional additional sensor.
#--------
sensor1External = AM2302
sensor1ExternalPin = 27
allSensors.insert(1, [sensor1External, sensor1ExternalPin, "external", "sensor1"])
#Sensor 4 - Optional additional sensor.
#--------
#sensor2External = AM2302
#sensor2ExternalPin = 0
#allSensors.insert(3, [sensor2External, sensor2ExternalPin, "external", "sensor2"])

#Specify A/C relay pins
fridgeRelayPin = 23
humidifierRelayPin = 24
dehumidifierRelayPin = 25
heaterRelayPin = 17
