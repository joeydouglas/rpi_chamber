#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sys
import requests

#---------
#Variables
#---------
#Database IP
dbIP = "192.168.1.220"
#Database port
dbPort = "8086"
#Influxdb database name
dbName = "test"
#Name of the curing chamber. Mostly useful if you have more than one.
chamberName = "meatsack"
#Desired temp/humidity set here.
desiredTemperature = 55
desiredHumidity = 80
#Set the drift or fluctuation allowed before outputs are changed to adjust the temp/humidity.
driftTemperature = 5
driftHumidity = 5


#Set timestamp in seconds. Only change if you need time accuracy beyond seconds.
seconds = int(time.time())

#Set GPIO pin specification. DO NOT CHANGE!
GPIO.setmode(GPIO.BCM)

#----------------------------
#Setup temp/humidity sensors.
#----------------------------
#Supported sensors. DO NOT CHANGE!
DHT11  = 11
DHT22  = 22
AM2302 = 22

#Setup variable for a sensor list. DO NOT CHANGE!
allSensors = [[]]

#Installed sensors. This will vary depending on your setup. Only one internal
#temp/humidity sensor is required. Uncomment/change the values for up to 4 sensors.
#Sensor 1
#--------
sensor1Internal = AM2302
sensor1InternalPin = 27
allSensors[0] = [sensor1Internal, sensor1InternalPin]
#Sensor 2
#--------
sensor2Internal = DHT22
sensor2InternalPin = 22
allSensors.insert(1, [sensor2Internal, sensor2InternalPin])
#Sensor 3
#--------
# sensor1External = Adafruit_DHT.AM2302
# sensor1ExternalPin = 30
# allSensors.insert(2, [sensor1External, sensor1ExternalPin])
#Sensor 4
#--------
# sensor2External = Adafruit_DHT.AM2302
# sensor2ExternalPin = 31
# allSensors.insert(3, [sensor2External, sensor2ExternalPin])


#Setup A/C relays and get current states.
#Refrigerator
fridgeRelayPin = 17
GPIO.setup(fridgeRelayPin,GPIO.OUT)
fridgeRelayState = GPIO.input(fridgeRelayPin)
#Humidifier
# humidifierRelayPin = 17
# GPIO.setup(fridgeRelayPin,GPIO.OUT)
# humidifierRelayState = GPIO.input(humidifierRelayPin)
#Dehumidifier
# dehumidifierRelayPin = 17
# GPIO.setup(fridgeRelayPin,GPIO.OUT)
# dehumidifierRelayState = GPIO.input(dehumidifierRelayPin)
#Heater
# heaterRelayPin = 17
# GPIO.setup(fridgeRelayPin,GPIO.OUT)
# heaterRelayState = GPIO.input(heaterRelayPin)

#Create Influxdb database
url = 'http://%s:%s/query' % (dbIP, dbPort)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = "q=CREATE DATABASE %s\n" % dbName
r = requests.post(url, data=payload, headers=headers)


#Function for getting temp/humidity readings.
def sensorReading():
  humidity, temperature = Adafruit_DHT.read_retry(allSensors[sensorIndex][0], allSensors[sensorIndex][1])
  if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    fahrenheitTemp = (temperature* 9)/5+32
    print fahrenheitTemp

    #output to influxdb
    url = 'http://%s:%s/write?db=%s&precision=s' % (dbIP, dbPort, dbName)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "temperature,area=internal,chamber=%s value=%d %d\n" % (chamberName, fahrenheitTemp, seconds)
    r = requests.post(url, data=payload, headers=headers)
    print payload
    payload2 = "humidity,area=internal,chamber=%s value=%d %d\n" % (chamberName, humidity, seconds)
    r = requests.post(url, data=payload2, headers=headers)
    print payload2
  else:
    print('Failed to get reading. Try again!')


#Loop through all sensors and get a reading.
for sensorIndex, val in enumerate(allSensors):
  print(sensorIndex)
  sensorReading()


#Cleanup GPIO entries.
GPIO.cleanup()
