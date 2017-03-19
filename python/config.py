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
db_ip = "192.168.1.30"
#Influxdb port. Default is 8086.
db_port = "8086"
#Influxdb database name
db_name = "meatsack"
#Name of the curing chamber. Mostly useful if you have more than one.
chamber_name = "meatsack"
#Desired temp/humidity set here.
desired_temperature = 15.5
desired_humidity = 80
#Set the drift or fluctuation allowed before outputs are changed to adjust the temp/humidity.
drift_temperature = 1
drift_humidity = 1
#How long should the program sleep in between sensor readings?
sensor_sleep = 5
#How long must the fridge be on/off for? This prevents the fridge from cycling on/off every few seconds.
fridge_cycle = 300
#Turn humidifier on and stall the fridge from turning on for a number of seconds to lessen the impact on the humidity.
fridge_stall = 20

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
all_sensors = [[]]

#Installed sensors. This will vary depending on your setup. Only one internal
#temp/humidity sensor (sensor1Internal) is required.
#Sensor 1 - Primary sensor - will determine which devices are turned on/off.
#--------
sensor_1_internal = SHT31_1
sensor_1_internal_pin = "i2c"
all_sensors[0] = [sensor_1_internal, sensor_1_internal_pin, "internal", "sensor1"]
#Sensor 2 - Optional additional sensor.
#--------
# sensor_2_internal = AM2302
# sensor_2_internal_pin = 22
#all_sensors.insert(1, [sensor_2_internal, sensor_2_internal_pin, "internal", "sensor2"])
#Sensor 3 - Optional additional sensor.
#--------
sensor_1_external = AM2302
sensor_1_external_pin = 27
all_sensors.insert(1, [sensor_1_external, sensor_1_external_pin, "external", "sensor1"])
#Sensor 4 - Optional additional sensor.
#--------
# sensor_2_external = AM2302
# sensor_2_external_pin = 0
# all_sensors.insert(3, [sensor_2_external, sensor_2_external_pin, "external", "sensor2"])

#Specify A/C relay pins
fridge_relay_pin = 23
humidifier_relay_pin = 24
dehumidifier_relay_pin = 25
heater_relay_pin = 17
