import config
import relay
import time
import requests
import Adafruit_DHT

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
      relay.relay_adjustments()
    #Output temp/humidity readings to Influxdb.
    influx_sensor_output()
  else:
    print('Failed to get reading. Try again!')

#Loop through all sensors and get a reading.
def sensor_loop():
  global sensor_index
  #global config.seconds
  for sensor_index, val in enumerate(config.all_sensors):
    config.seconds = int(time.time())
    if config.all_sensors[0]:
      relay.get_relay_state()
    sensor_reading()
    if config.all_sensors[sensor_index] == config.all_sensors[-1]:
      print "last sensor has been read, sleeping %s seconds.............................\n\n" % config.sensor_sleep
      time.sleep(config.sensor_sleep)


#Function to output temperature and humidity readings to Influxdb.
def influx_sensor_output():
  url = 'http://%s:%s/write?db=%s&precision=s' % (config.db_ip, config.db_port, config.db_name)
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  temperature_payload = "temperature,chamber=%s,sensor=%s,location=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamber_name, config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], config.desired_temperature, config.drift_temperature, temperature, config.seconds)
  print('Temp={0:0.1f}*C  Humidity={1:0.1f}%\n'.format(temperature, humidity))
  r = requests.post(url, data=temperature_payload, headers=headers)
  humidity_payload = "humidity,chamber=%s,sensor=%s,location=%s,desiredHumidity=%.1f,driftHumidity=%s value=%.1f %d\n" % (config.chamber_name, config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], config.desired_humidity, config.drift_humidity, humidity, config.seconds)
  r = requests.post(url, data=humidity_payload, headers=headers)
  #Influxdb doesn't allow you to query tags based on time so here's some redundant measurements. Wheeee!
  params_payload_temp = "params,chamber=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamber_name, config.desired_temperature, config.drift_temperature, config.desired_temperature, config.seconds)
  r = requests.post(url, data=params_payload_temp, headers=headers)