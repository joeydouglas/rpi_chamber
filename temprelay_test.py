#!/usr/bin/python
import RPi.GPIO as GPIO
import time
import Adafruit_DHT
import sys
import requests

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
    url = 'http://192.168.1.220:8086/write?db=meatsack'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = "tested04,host=%d,region=us-west value=0.64 1434055562000000000\n" % ftemp
    r = requests.post(url, data=payload, headers=headers)
else:
    print('Failed to get reading. Try again!')


#exit script if the temperature in Fahrenheit is less than 71 degrees, otherwise
if ftemp < 60.9:
    sys.exit()

GPIO.setmode(GPIO.BCM)

#setup relay output
number = 17
GPIO.setup(number,GPIO.OUT)
GPIO.output(number,GPIO.LOW)

# sleeptm = .25
try:
    state = GPIO.input(number)
    print state

#   GPIO.output(number, GPIO.LOW)
#   time.sleep(sleeptm);
#   GPIO.output(number, GPIO.HIGH)
#   time.sleep(sleeptm);
#   GPIO.output(number, GPIO.LOW)
#   time.sleep(sleeptm);
#   GPIO.output(number, GPIO.HIGH)
#   time.sleep(sleeptm);
#   GPIO.output(number, GPIO.LOW)
#   GPIO.cleanup()

except KeyboardInterrupt:
  GPIO.cleanup()
