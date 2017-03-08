#!/usr/bin/python
import config
import RPi.GPIO as GPIO
import time
from datetime import datetime
import sys
import requests
import Adafruit_DHT
from Adafruit_SHT31 import *

#Create Influxdb database. (This will probably be done when the Influxdb container is initialized, but for now....)
url = 'http://%s:%s/query' % (config.dbIP, config.dbPort)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = "q=CREATE DATABASE %s\n" % config.dbName
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
    url = 'http://%s:%s/write?db=%s&precision=s' % (config.dbIP, config.dbPort, config.dbName)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    self.RelayStatePayload = "%s,chamber=%s,stateChange=%d value=%d %d\n" % (self.name, config.chamberName, self.stateChange, self.relayState, config.seconds)
    r = requests.post(url, data=self.RelayStatePayload, headers=headers)

def getRelayState():
  #Create fridge object from Relayclass and get it's initial state.
  try:
    fridge
  except NameError:
    global fridge
    fridge = Relay("fridgeRelayState", config.fridgeRelayPin)
  fridge.setState(GPIO.input(fridge.pin))
  #Create heater object from Relayclass and get it's initial state.
  try:
    heater
  except NameError:
    global heater
    heater = Relay("heaterRelayState", config.heaterRelayPin)
  heater.setState(GPIO.input(heater.pin))
  #Create humidifier object from Relayclass and get it's initial state.
  try:
    humidifier
  except NameError:
    global humidifier
    humidifier = Relay("humidifierRelayState", config.humidifierRelayPin)
  humidifier.setState(GPIO.input(humidifier.pin))
  humidifier.setOverride(0)
  #Create dehumidifier object from Relayclass and get it's initial state.
  try:
    dehumidifier
  except NameError:
    global dehumidifier
    dehumidifier = Relay("dehumidifierRelayState", config.dehumidifierRelayPin)
  dehumidifier.setState(GPIO.input(dehumidifier.pin))

#Functions for turning devices on/off.
def humidifierOn():
  humidifier.updateState(1)
  GPIO.output(humidifier.pin,humidifier.relayState)
  humidifier.influxRelayOutput()
def humidifierOff():
  if fridge.relayState == 0:
    humidifier.updateState(0)
    GPIO.output(humidifier.pin,humidifier.relayState)
  humidifier.influxRelayOutput()
def fridgeOn():
  humidifier.setOverride(1)
  humidifierOn()
  fridge.stallTimerCreate()
  fridge.stallTimerUpdate()
  stallTimer = fridge.stallStop - fridge.stallStart
  while (stallTimer.total_seconds() < config.fridgeStall):
    print 'Running Humidifier for %d seconds before turning on Fridge*********' % config.fridgeStall
    print stallTimer.total_seconds()
    time.sleep(5)
    fridge.stallTimerUpdate()
    stallTimer = fridge.stallStop - fridge.stallStart
  humidifier.setOverride(0)
  fridgeOnFinal()
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
  print "Reading %s, %s (ID %d)" % (config.allSensors[sensorIndex][3], config.allSensors[sensorIndex][2], sensorIndex)
  global temperature, humidity
  #Commented out code to get reading from DHT sensors.
  if config.allSensors[sensorIndex][1] == "i2c":
    temperature = config.sensor1Internal.read_temperature()
    humidity = config.sensor1Internal.read_humidity()
  else:
    humidity, temperature = Adafruit_DHT.read_retry(config.allSensors[sensorIndex][0], config.allSensors[sensorIndex][1])
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
  url = 'http://%s:%s/write?db=%s&precision=s' % (config.dbIP, config.dbPort, config.dbName)
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  temperaturePayload = "temperature,chamber=%s,sensor=%s,location=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamberName, config.allSensors[sensorIndex][3], config.allSensors[sensorIndex][2], config.desiredTemperature, config.driftTemperature, temperature, config.seconds)
  print('Temp={0:0.1f}*C  Humidity={1:0.1f}%\n'.format(temperature, humidity))
  r = requests.post(url, data=temperaturePayload, headers=headers)
  #print temperaturePayload
  humidityPayload = "humidity,chamber=%s,sensor=%s,location=%s,desiredHumidity=%.1f,driftHumidity=%s value=%.1f %d\n" % (config.chamberName, config.allSensors[sensorIndex][3], config.allSensors[sensorIndex][2], config.desiredHumidity, config.driftHumidity, humidity, config.seconds)
  r = requests.post(url, data=humidityPayload, headers=headers)
  #Influxdb doesn't allow you to query tags based on time so here's some redundant measurements. Wheeee!
  paramsPayloadTemp = "params,chamber=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamberName, config.desiredTemperature, config.driftTemperature, config.desiredTemperature, config.seconds)
  r = requests.post(url, data=paramsPayloadTemp, headers=headers)

def fridgeCycleOn():
  if hasattr(fridge, 'startTimer'):
    fridge.updateTimer()
    fridgeTimer = fridge.stopTimer - fridge.startTimer
    print "Fridge Cycle Timer------------%d" % (fridgeTimer.total_seconds())
    if (fridgeTimer.total_seconds() > config.fridgeCycle) and (fridge.relayState == 0):
      print "Fridge cycle length has been met."
      fridgeOn()
      print "Fridge turning on!"
  else:
    fridgeOn()

def fridgeCycleOff():
  if hasattr(fridge, 'startTimer'):
    fridge.updateTimer()
    fridgeTimer = fridge.stopTimer - fridge.startTimer
    print "Fridge Cycle Timer------------%d" % (fridgeTimer.total_seconds())
    if (fridgeTimer.total_seconds() > config.fridgeCycle) and (fridge.relayState == 1):
      print "Fridge has been on long enough!!!!!!!!!!!!!!!!!"
      fridgeOff()
      print "Fridge turning off!"
  else:
    fridgeOff()

#Function to set relays based on sensor readings.
def relayAdjustments():
  #Temperature (Fridge and heater).
  if temperature > (config.desiredTemperature + config.driftTemperature):
    fridgeCycleOn()
    heaterOff()
    print "Temperature too high. Turning on refrigerator."
  elif temperature < (config.desiredTemperature - config.driftTemperature):
    fridgeCycleOff()
    heaterOn()
    print "Temperature too low. Turning off refrigerator."
  elif (config.desiredTemperature - config.driftTemperature) <= temperature <= (config.desiredTemperature + config.driftTemperature):
    fridgeCycleOff()
    heaterOff()
    print "Temperature is within range!"

  #Humidity (Humidifier and dehumidifier).
  if humidity is not None and humidity < 105:
    if humidity > (config.desiredHumidity + config.driftHumidity):
      if fridge.relayState == 1: #we always want the humifier on if the fridge is on.
        humidifierOn()
        dehumidifierOff()
      elif (fridge.relayState == 0) and (humidifier.override != 1): #don't turn off the humidifier if the override is on.
        humidifierOff()
        dehumidifierOn()
      print "Humidity too high. Turning off humidifier."
    elif humidity < (config.desiredHumidity - config.driftHumidity):
      humidifierOn()
      dehumidifierOff()
      print "Humidity too low. Turning on humidifier."
    elif ((config.desiredHumidity - config.driftHumidity) <= humidity <= (config.desiredHumidity + config.driftHumidity)) and (humidifier.override != 1):
      humidifierOff()
      dehumidifierOff()
      print "Humidity is within range!"
    else:
      print "Humidity is within range!"

#Loop through all sensors and get a reading.
def sensorLoop():
  global sensorIndex
  #global config.seconds
  for sensorIndex, val in enumerate(config.allSensors):
    config.seconds = int(time.time())
    if config.allSensors[0]:
      getRelayState()
    sensorReading()
    if config.allSensors[sensorIndex] == config.allSensors[-1]:
      print "last sensor has been read, sleeping %s seconds.............................\n\n" % config.sensorSleep
      print humidifier.override
      time.sleep(config.sensorSleep)

#Run this sucker continually.
infiniteLoop = 1
while infiniteLoop == 1:
  sensorLoop()
