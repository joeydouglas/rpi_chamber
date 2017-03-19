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
url = 'http://%s:%s/query' % (config.db_ip, config.db_port)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = "q=CREATE DATABASE %s\n" % config.db_name
r = requests.post(url, data=payload, headers=headers)

#Create class for watching relay states.
class Relay:
  def __init__(self, name, pin):
    self.pin = pin
    self.name = name
    print self.name
    GPIO.setup(self.pin,GPIO.OUT)
  def set_state(self, state):
    self.relay_state = state
    self.state_change = 0
  def udpate_state(self, new_state):
    if self.relay_state != new_state:
      self.state_change = 1
      self.relay_state = new_state
      self.start_timer = datetime.now()
    else:
      self.state_change = 0
      self.relay_state = new_state
  def update_timer(self):
    self.stop_timer = datetime.now()
  def stall_timer_create(self):
    self.stallStart = datetime.now()
  def stall_timer_update(self):
    self.stallStop = datetime.now()
  def set_override(self, override):
    self.override = override
  def influx_relay_output(self):
    url = 'http://%s:%s/write?db=%s&precision=s' % (config.db_ip, config.db_port, config.db_name)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    self.relay_state_payload = "%s,chamber=%s,stateChange=%d value=%d %d\n" % (self.name, config.chamber_name, self.state_change, self.relay_state, config.seconds)
    r = requests.post(url, data=self.relay_state_payload, headers=headers)

def get_relay_state():
  #Create fridge object from Relay class and get it's initial state.
  try:
    fridge
  except NameError:
    global fridge
    fridge = Relay("fridge_relay_state", config.fridge_relay_pin)
  fridge.set_state(GPIO.input(fridge.pin))
  #Create heater object from Relay class and get it's initial state.
  try:
    heater
  except NameError:
    global heater
    heater = Relay("heater_relay_state", config.heater_relay_pin)
  heater.set_state(GPIO.input(heater.pin))
  #Create humidifier object from Relay class and get it's initial state.
  try:
    humidifier
  except NameError:
    global humidifier
    humidifier = Relay("humidifier_relay_state", config.humidifier_relay_pin)
  humidifier.set_state(GPIO.input(humidifier.pin))
  humidifier.set_override(0)
  #Create dehumidifier object from Relay class and get it's initial state.
  try:
    dehumidifier
  except NameError:
    global dehumidifier
    dehumidifier = Relay("dehumidifier_relay_state", config.dehumidifier_relay_pin)
  dehumidifier.set_state(GPIO.input(dehumidifier.pin))

#Functions for turning devices on/off.
def humidifier_on():
  humidifier.udpate_state(1)
  GPIO.output(humidifier.pin, humidifier.relay_state)
  humidifier.influx_relay_output()
def humidifier_off():
  if fridge.relay_state == 0:
    humidifier.udpate_state(0)
    GPIO.output(humidifier.pin, humidifier.relay_state)
  humidifier.influx_relay_output()
def fridge_on():
  humidifier.set_override(1)
  humidifier_on()
  fridge.stall_timer_create()
  fridge.stall_timer_update()
  stall_timer = fridge.stallStop - fridge.stallStart
  while (stall_timer.total_seconds() < config.fridge_stall):
    print 'Running Humidifier for %d seconds before turning on Fridge*********' % config.fridge_stall
    print stall_timer.total_seconds()
    time.sleep(5)
    fridge.stall_timer_update()
    stall_timer = fridge.stallStop - fridge.stallStart
  humidifier.set_override(0)
  fridge_on_final()
def fridge_on_final():
  fridge.udpate_state(1)
  GPIO.output(fridge.pin, fridge.relay_state)
  fridge.influx_relay_output()
def fridge_off():
  fridge.udpate_state(0)
  GPIO.output(fridge.pin, fridge.relay_state)
  fridge.influx_relay_output()
def heater_on():
  heater.udpate_state(1)
  GPIO.output(heater.pin, heater.relay_state)
  heater.influx_relay_output()
def heater_off():
  heater.udpate_state(0)
  GPIO.output(heater.pin, heater.relay_state)
  heater.influx_relay_output()
def dehumidifier_on():
  dehumidifier.udpate_state(1)
  GPIO.output(dehumidifier.pin, dehumidifier.relay_state)
  dehumidifier.influx_relay_output()
def dehumidifier_off():
  dehumidifier.udpate_state(0)
  GPIO.output(dehumidifier.pin, dehumidifier.relay_state)
  dehumidifier.influx_relay_output()

#Function for getting temp/humidity readings.
def sensor_reading():
  print "Reading %s, %s (ID %d)" % (config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], sensor_index)
  global temperature, humidity
  #Commented out code to get reading from DHT sensors.
  if config.all_sensors[sensor_index][1] == "i2c":
    temperature = config.sensor_1_internal.read_temperature()
    humidity = config.sensor_1_internal.read_humidity()
  else:
    humidity, temperature = Adafruit_DHT.read_retry(config.all_sensors[sensor_index][0], config.all_sensors[sensor_index][1])
#Ensure you get a reading from the sensor before continuing.
  if humidity is not None and temperature is not None:
    #Adjust relay states based on primary sensor(0) reading.
    if sensor_index is 0:
      relay_adjustments()
    #Output temp/humidity readings to Influxdb.
    influx_sensor_output()
  else:
    print('Failed to get reading. Try again!')

#Function to output temperature and humidity readings to Influxdb.
def influx_sensor_output():
  url = 'http://%s:%s/write?db=%s&precision=s' % (config.db_ip, config.db_port, config.db_name)
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  temperature_payload = "temperature,chamber=%s,sensor=%s,location=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamber_name, config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], config.desired_temperature, config.drift_temperature, temperature, config.seconds)
  print('Temp={0:0.1f}*C  Humidity={1:0.1f}%\n'.format(temperature, humidity))
  r = requests.post(url, data=temperature_payload, headers=headers)
  #print temperature_payload
  humidity_payload = "humidity,chamber=%s,sensor=%s,location=%s,desiredHumidity=%.1f,driftHumidity=%s value=%.1f %d\n" % (config.chamber_name, config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], config.desired_humidity, config.drift_humidity, humidity, config.seconds)
  r = requests.post(url, data=humidity_payload, headers=headers)
  #Influxdb doesn't allow you to query tags based on time so here's some redundant measurements. Wheeee!
  params_payload_temp = "params,chamber=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamber_name, config.desired_temperature, config.drift_temperature, config.desired_temperature, config.seconds)
  r = requests.post(url, data=params_payload_temp, headers=headers)

def fridge_cycle_on():
  if hasattr(fridge, 'startTimer'):
    fridge.update_timer()
    fridge_timer = fridge.stop_timer - fridge.start_timer
    print "Fridge Cycle Timer------------%d" % (fridge_timer.total_seconds())
    if (fridge_timer.total_seconds() > config.fridge_cycle) and (fridge.relay_state == 0):
      print "Fridge cycle length has been met."
      fridge_on()
      print "Fridge turning on!"
  else:
    fridge_on()

def fridge_cycle_off():
  if hasattr(fridge, 'startTimer'):
    fridge.update_timer()
    fridge_timer = fridge.stop_timer - fridge.start_timer
    print "Fridge Cycle Timer------------%d" % (fridge_timer.total_seconds())
    if (fridge_timer.total_seconds() > config.fridge_cycle) and (fridge.relay_state == 1):
      print "Fridge has been on long enough!!!!!!!!!!!!!!!!!"
      fridge_off()
      print "Fridge turning off!"
  else:
    fridge_off()

#Function to set relays based on sensor readings.
def relay_adjustments():
  #Temperature (Fridge and heater).
  if temperature > (config.desired_temperature + config.drift_temperature):
    fridge_cycle_on()
    heater_off()
    print "Temperature too high. Turning on refrigerator."
  elif temperature < (config.desired_temperature - config.drift_temperature):
    fridge_cycle_off()
    heater_on()
    print "Temperature too low. Turning off refrigerator."
  elif (config.desired_temperature - config.drift_temperature) <= temperature <= (config.desired_temperature + config.drift_temperature):
    fridge_cycle_off()
    heater_off()
    print "Temperature is within range!"

  #Humidity (Humidifier and dehumidifier).
  if humidity is not None and humidity < 105:
    if humidity > (config.desired_humidity + config.drift_humidity):
      if fridge.relay_state == 1: #we always want the humidifier on if the fridge is on.
        humidifier_on()
        dehumidifier_off()
      elif (fridge.relay_state == 0) and (humidifier.override != 1): #don't turn off the humidifier if the override is on.
        humidifier_off()
        dehumidifier_on()
      print "Humidity too high. Turning off humidifier."
    elif humidity < (config.desired_humidity - config.drift_humidity):
      humidifier_on()
      dehumidifier_off()
      print "Humidity too low. Turning on humidifier."
    elif ((config.desired_humidity - config.drift_humidity) <= humidity <= (config.desired_humidity + config.drift_humidity)) and (humidifier.override != 1):
      humidifier_off()
      dehumidifier_off()
      print "Humidity is within range!"
    else:
      print "Humidity is within range!"

#Loop through all sensors and get a reading.
def sensor_loop():
  global sensor_index
  #global config.seconds
  for sensor_index, val in enumerate(config.all_sensors):
    config.seconds = int(time.time())
    if config.all_sensors[0]:
      get_relay_state()
    sensor_reading()
    if config.all_sensors[sensor_index] == config.all_sensors[-1]:
      print "last sensor has been read, sleeping %s seconds.............................\n\n" % config.sensor_sleep
      print humidifier.override
      time.sleep(config.sensor_sleep)

#Run this sucker continually.
infinite_loop = 1
while infinite_loop == 1:
  sensor_loop()
