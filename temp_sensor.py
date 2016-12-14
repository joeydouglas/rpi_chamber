import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sys
import requests

#TIME! Got the time ti-ti-tickin in my head!
seconds = int(time.time())
print seconds

#setup temp/humidity sensor
sensor = Adafruit_DHT.AM2302
pin = 27

#grab temp/humidity readings
humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    print temperature
    ctemp = temperature
    ftemp = (ctemp* 9)/5+32
    print ftemp
   
    #output to influxdb
    url = 'http://192.168.1.220:8086/write?db=meatsack&precision=s'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "temperature,area=internal,chamber=meatsack value=%d %d\n" % (ftemp, seconds)
    r = requests.post(url, data=payload, headers=headers)
    payload2 = "humidity,area=internal,chamber=meatsack value=%d %d\n" % (humidity, seconds)
    print payload
    r = requests.post(url, data=payload2, headers=headers)
    print payload2
else:
    print('Failed to get reading. Try again!')

