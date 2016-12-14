#!/usr/bin/python

import Adafruit_DHT

sensor = Adafruit_DHT.AM2302
pin = 22


humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
if humidity is not None and temperature is not None:
    print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity))
    print temperature
    ctemp = temperature
    ftemp = (ctemp* 9)/5+32
    print ftemp
else:
    print('Failed to get reading. Try again!')
