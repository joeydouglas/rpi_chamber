#!/usr/bin/python
import RPi.GPIO as GPIO
import time
from datetime import datetime
#from timeit import default_timer as timer
import sys
#import math
import requests
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
fridgeCycle = 60


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
#SHT31_2 = SHT31(address = 0x45)

#Setup variable for a sensor list. DO NOT CHANGE!
allSensors = [[]]

#Installed sensors. This will vary depending on your setup. Only one internal
#temp/humidity sensor is required. Uncomment/change the values for up to 4 sensors.
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

#----------------------------------------
#Setup A/C relays and get current states.
#----------------------------------------
#Refrigerator
fridgeRelayPin = 23
#Humidifier
humidifierRelayPin = 24
#Dehumidifier
dehumidifierRelayPin = 25
#Heater
heaterRelayPin = 17


##########################################################################
#DO NOT EDIT BELOW This
##########################################################################

#Create Influxdb database. (This will probably be done when the Influxdb container is initialized, but for now....)
url = 'http://%s:%s/query' % (dbIP, dbPort)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = "q=CREATE DATABASE %s\n" % dbName
r = requests.post(url, data=payload, headers=headers)


#Create class for watching relay states.
class Relay:
  def __init__(self, name, pin):
    self.pin = pin
    self.name = name
    print self.name
    GPIO.setup(self.pin,GPIO.OUT)
  def setState(self, state):
    self.relayState = state
    self.stateChange = 0
  def updateState(self, newState):
    if self.relayState != newState:
      self.stateChange = 1
      self.relayState = newState
      self.startTimer = datetime.now()
    else:
      self.stateChange = 0
      self.relayState = newState
  def updateTimer(self):
    self.stopTimer = datetime.now()
  def stallTimerCreate(self):
    self.stallStart = datetime.now()
  def stallTimerUpdate(self):
    self.stallStop = datetime.now()
  def setOverride(self, override):
    self.override = override
  def influxRelayOutput(self):
    url = 'http://%s:%s/write?db=%s&precision=s' % (dbIP, dbPort, dbName)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    self.RelayStatePayload = "%s,chamber=%s,stateChange=%d value=%d %d\n" % (self.name, chamberName, self.stateChange, self.relayState, seconds)
    r = requests.post(url, data=self.RelayStatePayload, headers=headers)

def getRelayState():
  #Create fridge object from Relayclass and get it's initial state.
  try:
    fridge
  except NameError:
    global fridge
    fridge = Relay("fridgeRelayState", fridgeRelayPin)
  fridge.setState(GPIO.input(fridge.pin))

  #Create heater object from Relayclass and get it's initial state.
  try:
    heater
  except NameError:
    global heater
    heater = Relay("heaterRelayState", heaterRelayPin)
  heater.setState(GPIO.input(heater.pin))

  #Create humidifier object from Relayclass and get it's initial state.
  try:
    humidifier
  except NameError:
    global humidifier
    humidifier = Relay("humidifierRelayState", humidifierRelayPin)
  humidifier.setState(GPIO.input(humidifier.pin))
  humidifier.setOverride(0)

  #Create dehumidifier object from Relayclass and get it's initial state.
  try:
    dehumidifier
  except NameError:
    global dehumidifier
    dehumidifier = Relay("dehumidifierRelayState", dehumidifierRelayPin)
  dehumidifier.setState(GPIO.input(dehumidifier.pin))


#Functions for turning devices on/off.
def humidifierOn():
  humidifier.updateState(1)
  GPIO.output(humidifier.pin,humidifier.relayState)
  humidifier.influxRelayOutput()
def humidifierOff():
  humidifier.updateState(0)
  GPIO.output(humidifier.pin,humidifier.relayState)
  humidifier.influxRelayOutput()
  #humidifier.override(0)
def fridgeOn():
  humidifier.setOverride(1)
  humidifierOn()
  fridgeStall = 20
  fridge.stallTimerCreate()
  fridge.stallTimerUpdate()
  stallTimer = fridge.stallStop - fridge.stallStart
  while (stallTimer.total_seconds() < fridgeStall):
    print 'Running Humidifier for 30 seconds before turning on Fridge*********'
    print stallTimer.total_seconds()
    time.sleep(5)
    fridge.stallTimerUpdate()
    stallTimer = fridge.stallStop - fridge.stallStart
  fridgeOnFinal()
  humidifier.setOverride(0)
def fridgeOnFinal():
  fridge.updateState(1)
  GPIO.output(fridge.pin,fridge.relayState)
  fridge.influxRelayOutput()
def fridgeOff():
  fridge.updateState(0)
  GPIO.output(fridge.pin,fridge.relayState)
  fridge.influxRelayOutput()
def heaterOn():
  heater.updateState(1)
  GPIO.output(heater.pin,heater.relayState)
  heater.influxRelayOutput()
def heaterOff():
  heater.updateState(0)
  GPIO.output(heater.pin,heater.relayState)
  heater.influxRelayOutput()
def dehumidifierOn():
  dehumidifier.updateState(1)
  GPIO.output(dehumidifier.pin,dehumidifier.relayState)
  dehumidifier.influxRelayOutput()
def dehumidifierOff():
  dehumidifier.updateState(0)
  GPIO.output(dehumidifier.pin,dehumidifier.relayState)
  dehumidifier.influxRelayOutput()


#Function for getting temp/humidity readings.
def sensorReading():
  print "Reading %s, %s (ID %d)" % (allSensors[sensorIndex][3], allSensors[sensorIndex][2], sensorIndex)
  global temperature, humidity
  #Commented out code to get reading from DHT sensors.
  if allSensors[sensorIndex][1] == "i2c":
    temperature = sensor1Internal.read_temperature()
    humidity = sensor1Internal.read_humidity()
  else:
    humidity, temperature = Adafruit_DHT.read_retry(allSensors[sensorIndex][0], allSensors[sensorIndex][1])
#Ensure you get a reading from the sensor before continuing.
  if humidity is not None and temperature is not None:
    #Adjust relay states based on primary sensor(0) reading.
    if sensorIndex is 0:
      relayAdjustments()
    #Output temp/humidity readings to Influxdb.
    influxSensorOutput()
  else:
    print('Failed to get reading. Try again!')


#Function to output temperature and humidity readings to Influxdb.
def influxSensorOutput():
  url = 'http://%s:%s/write?db=%s&precision=s' % (dbIP, dbPort, dbName)
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  temperaturePayload = "temperature,chamber=%s,sensor=%s,location=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (chamberName, allSensors[sensorIndex][3], allSensors[sensorIndex][2], desiredTemperature, driftTemperature, temperature, seconds)
  print('Temp={0:0.1f}*C  Humidity={1:0.1f}%\n'.format(temperature, humidity))
  r = requests.post(url, data=temperaturePayload, headers=headers)
  #print temperaturePayload
  humidityPayload = "humidity,chamber=%s,sensor=%s,location=%s,desiredHumidity=%.1f,driftHumidity=%s value=%.1f %d\n" % (chamberName, allSensors[sensorIndex][3], allSensors[sensorIndex][2], desiredHumidity, driftHumidity, humidity, seconds)
  r = requests.post(url, data=humidityPayload, headers=headers)
  #Influxdb doesn't allow you to query tags based on time so here's some redundant measurements. Wheeee!
  paramsPayloadTemp = "params,chamber=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (chamberName, desiredTemperature, driftTemperature, desiredTemperature, seconds)
  r = requests.post(url, data=paramsPayloadTemp, headers=headers)


#Function to set relays based on sensor readings.
def relayAdjustments():
  #Temperature (Fridge and heater).
  if temperature > (desiredTemperature + driftTemperature):
    if hasattr(fridge, 'startTimer'):
      print "FRIDGE Timer-----"
      fridge.updateTimer()
      fridgeTimer = fridge.stopTimer - fridge.startTimer
      print(fridgeTimer.total_seconds())
      if (fridgeTimer.total_seconds() > fridgeCycle) and (fridge.relayState == 0):
        print "Fridge has been off long enough!!!!!!!!!!!!!!!!!"
        fridgeOn()
        print "Fridge turning on!"
    else:
      fridgeOn()
    heaterOff()
    print "Temperature too high. Turning on refrigerator."
  elif temperature < (desiredTemperature - driftTemperature):
    if hasattr(fridge, 'startTimer'):
      print "FRIDGE Timer-----"
      fridge.updateTimer()
      fridgeTimer = fridge.stopTimer - fridge.startTimer
      print(fridgeTimer.total_seconds())
      if (fridgeTimer.total_seconds() > fridgeCycle) and (fridge.relayState == 1):
        print "Fridge has been on long enough!!!!!!!!!!!!!!!!!"
        fridgeOff()
        print "Fridge turning off!"
    else:
      fridgeOff()
    heaterOn()
    print "Temperature too low. Turning off refrigerator."
  elif (desiredTemperature - driftTemperature) <= temperature <= (desiredTemperature + driftTemperature):
    if hasattr(fridge, 'startTimer'):
      print "FRIDGE Timer-----"
      fridge.updateTimer()
      fridgeTimer = fridge.stopTimer - fridge.startTimer
      print(fridgeTimer.total_seconds())
      if (fridgeTimer.total_seconds() > fridgeCycle) and (fridge.relayState == 1):
        print "Fridge has been on long enough!!!!!!!!!!!!!!!!!!!!"
        fridgeOff()
        print "Fridge turning off!"
    else:
      fridgeOff()
    heaterOff()
    print "Temperature is within range!"
  else:
    print "Temperature is within range!"

  #Humidity (Humidifier and dehumidifier).
  if humidity is not None and humidity < 105:
    if humidity > (desiredHumidity + driftHumidity):
      if fridge.relayState == 1:
        humidifierOn()
        dehumidifierOff()
      elif (fridge.relayState == 0) and (humidifier.override != 1):
        humidifierOff()
        dehumidifierOn()
      print "Humidity too high. Turning off humidifier."
    elif humidity < (desiredHumidity - driftHumidity):
      humidifierOn()
      dehumidifierOff()
      print "Humidity too low. Turning on humidifier."
    elif ((desiredHumidity - driftHumidity) <= humidity <= (desiredHumidity + driftHumidity)) and (humidifier.override != 1):
      humidifierOff()
      dehumidifierOff()
      print "Humidity is within range!"
    else:
      print "Humidity is within range!"


#Loop through all sensors and get a reading.
def sensorLoop():
  global sensorIndex
  global seconds
  for sensorIndex, val in enumerate(allSensors):
    seconds = int(time.time())
    if allSensors[0]:
      getRelayState()
    sensorReading()
    #time.sleep(3)
    if allSensors[sensorIndex] == allSensors[-1]:
      print "last sensor has been read, sleeping %s seconds.............................\n\n" %sensorSleep
      print humidifier.override
      time.sleep(sensorSleep)

#Run this sucker continually.
infiniteLoop = 1
while infiniteLoop == 1:
  sensorLoop()
