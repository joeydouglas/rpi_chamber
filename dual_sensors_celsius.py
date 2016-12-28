import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sys
import requests

#TIME! Got the time ti-ti-tickin in my head!
seconds = int(time.time())
print seconds

#setup am2302 temp/humidity sensor
sensor1 = Adafruit_DHT.AM2302
pin1 = 27


#setup dht22 temp/humidity sensor
sensor2 = Adafruit_DHT.DHT22
pin2 = 22

#grab temp/humidity readings from am2302
humidity, temperature = Adafruit_DHT.read_retry(sensor1, pin1)
if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    print temperature
    ctemp = temperature
    ftemp = (ctemp* 9)/5+32
    print ftemp
   
    #output to influxdb
    url = 'http://192.168.1.30:8086/write?db=meatsack&precision=s'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "temperature,area=internal,chamber=meatsack value=%.1f %d\n" % (temperature, seconds)
    r = requests.post(url, data=payload, headers=headers)
    payload2 = "humidity,area=internal,chamber=meatsack value=%.1f %d\n" % (humidity, seconds)
    print payload
    r = requests.post(url, data=payload2, headers=headers)
    print payload2
else:
    print('Failed to get reading. Try again!')

#grab temp/humidity readings from dht22 
humidity, temperature = Adafruit_DHT.read_retry(sensor2, pin2)
if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    print temperature
    ctemp = temperature
    ftemp = (ctemp* 9)/5+32
    print ftemp
   
    #output to influxdb
    url = 'http://192.168.1.30:8086/write?db=meatsack&precision=s'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "temperature2,area=internal,chamber=meatsack value=%.1f %d\n" % (temperature, seconds)
    r = requests.post(url, data=payload, headers=headers)
    payload2 = "humidity2,area=internal,chamber=meatsack value=%.1f %d\n" % (humidity, seconds)
    print payload
    r = requests.post(url, data=payload2, headers=headers)
    print payload2
else:
    print('Failed to get reading. Try again!')
