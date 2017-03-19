import config


#Function to output temperature and humidity readings to Influxdb.
def influx_sensor_output():
  url = 'http://%s:%s/write?db=%s&precision=s' % (config.db_ip, config.db_port, config.db_name)
  headers = {'Content-Type': 'application/x-www-form-urlencoded'}
  temperature_payload = "temperature,chamber=%s,sensor=%s,location=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamber_name, config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], config.desired_temperature, config.drift_temperature, main.temperature, config.seconds)
  print('Temp={0:0.1f}*C  Humidity={1:0.1f}%\n'.format(temperature, humidity))
  r = requests.post(url, data=temperature_payload, headers=headers)
  #print temperature_payload
  humidity_payload = "humidity,chamber=%s,sensor=%s,location=%s,desiredHumidity=%.1f,driftHumidity=%s value=%.1f %d\n" % (config.chamber_name, config.all_sensors[sensor_index][3], config.all_sensors[sensor_index][2], config.desired_humidity, config.drift_humidity, main.humidity, config.seconds)
  r = requests.post(url, data=humidity_payload, headers=headers)
  #Influxdb doesn't allow you to query tags based on time so here's some redundant measurements. Wheeee!
  params_payload_temp = "params,chamber=%s,desiredTemperature=%.1f,driftTemperature=%s value=%.1f %d\n" % (config.chamber_name, config.desired_temperature, config.drift_temperature, config.desired_temperature, config.seconds)
  r = requests.post(url, data=params_payload_temp, headers=headers)

