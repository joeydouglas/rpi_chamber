#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sys
import requests

#Variables
#Name of the curing chamber.
chamber = "meatsack"
#Desired temp/humidity set here.
desired_temperature = 55
desired_humidity = 80
#Set the drift or fluctuation allowed before outputs are changed to adjust the temp/humidity.
drift_temperature = 5
drive_humidity = 5


#Set timestamp in seconds. (TIME! Got the time ti-ti-tickin in my head!)
seconds = int(time.time())

#Set GPIO pin specification
GPIO.setmode(GPIO.BCM)

#Setup temp/humidity sensors. Only one is necessary. Dual internal and external provides peace of mind.
#Supported sensors
DHT11  = 11
DHT22  = 22
AM2302 = 22
#Used sensors
sensor1_internal = AM2302
sensor1_internal_pin = 27
#sensor1 = (sensor1_internal, sensor1_internal_pin)

sensor2_internal = DHT22
sensor2_internal_pin = 22
#
# sensor1_external = Adafruit_DHT.AM2302
# sensor1_external_pin = 27
#
# sensor2_external = Adafruit_DHT.AM2302
# sensor2_external_pin = 27
all_sensors = [
  [sensor1_internal, sensor1_internal_pin],
  [sensor2_internal, sensor2_internal_pin]
  ]

# row = 0
# rowList = all_sensors[row]
print all_sensors[1][1]

# for sensor in all_sensors:
#   print all_sensors[]
#   # if sensor is not None:
  #   print "%s sensor exists" % sensor


#Setup A/C relays and get current states.
#Refrigerator
fridge_relay_pin = 17
GPIO.setup(fridge_relay_pin,GPIO.OUT)
fridge_relay_state = GPIO.input(fridge_relay_pin)
#Humidifier
# humidifier_relay_pin = 17
# GPIO.setup(fridge_relay_pin,GPIO.OUT)
# humidifier_relay_state = GPIO.input(humidifier_relay_pin)
#Dehumidifier
# dehumidifier_relay_pin = 17
# GPIO.setup(fridge_relay_pin,GPIO.OUT)
# dehumidifier_relay_state = GPIO.input(dehumidifier_relay_pin)
#Heater
# heater_relay_pin = 17
# GPIO.setup(fridge_relay_pin,GPIO.OUT)
# heater_relay_state = GPIO.input(heater_relay_pin)





#Function for getting temp/humidity readings.
def sensorReading():
  humidity, temperature = Adafruit_DHT.read_retry(all_sensors[sensor_index][0], all_sensors[sensor_index][1])
  if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    fahrenheit_temp = (temperature* 9)/5+32
    print fahrenheit_temp

    #output to influxdb
    # url = 'http://192.168.1.220:8086/write?db=meatsack&precision=s'
    # headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    # payload = "temperature,area=internal,chamber=meatsack value=%d %d\n" % (ftemp, seconds)
    # r = requests.post(url, data=payload, headers=headers)
    # payload2 = "humidity,area=internal,chamber=meatsack value=%d %d\n" % (humidity, seconds)
    # print payload
    # r = requests.post(url, data=payload2, headers=headers)
    # print payload2
  else:
    print('Failed to get reading. Try again!')

#Loop through all sensors and get a reading.
for sensor_index, val in enumerate(all_sensors):
  print(sensor_index)
  sensorReading()


#Cleanup GPIO entries.
GPIO.cleanup()
