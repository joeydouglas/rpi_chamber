#!/usr/bin/python
import requests
import config
import sensor


url = 'http://%s:%s/query' % (config.db_ip, config.db_port)
headers = {'Content-Type': 'application/x-www-form-urlencoded'}
payload = "q=CREATE DATABASE %s\n" % config.db_name
r = requests.post(url, data=payload, headers=headers)


#Run this sucker continually.
infinite_loop = 1
while infinite_loop == 1:
  sensor.sensor_loop()
