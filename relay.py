import config
import RPi.GPIO as GPIO
import requests
from datetime import datetime
import time
import sensor


class Relay:
  def __init__(self, name, pin):
    self.pin = pin
    self.name = name
    print 'Creating %s' % self.name
    GPIO.setup(self.pin,GPIO.OUT)
  def set_state(self, state):
    self.relay_state = state
    self.state_change = 0
  def udpate_state(self, new_state):
    if self.relay_state != new_state:
      self.state_change = 1
      self.relay_state = new_state
      if new_state == 0:
          self.state_name = 'off'
      elif new_state == 1:
          self.state_name = 'on'
      self.start_timer = datetime.now()
      print "%s is now %s" % (self.name, self.state_name)
    else:
      self.state_change = 0
      self.relay_state = new_state
  def update_timer(self):
    self.stop_timer = datetime.now()
  def stall_timer_create(self):
    self.stallStart = datetime.now()
  def stall_timer_update(self):
    self.stall_stop = datetime.now()
  def set_override(self, override):
    self.override = override
  def influx_relay_output(self):
    url = 'http://%s:%s/write?db=%s&precision=s' % (config.db_ip, config.db_port, config.db_name)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    self.relay_state_payload = "%s,chamber=%s,state_change=%d value=%d %d\n" % (self.name, config.chamber_name, self.state_change, self.relay_state, config.seconds)
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


#-------------------------------------
#Functions for turning devices on/off.
#-------------------------------------
def humidifier_on():
  humidifier.udpate_state(1)
  GPIO.output(humidifier.pin, humidifier.relay_state)
  humidifier.influx_relay_output()


def humidifier_off():
  #Do not turn off humidifier if fridge is running.
  if fridge.relay_state == 0:
    humidifier.udpate_state(0)
    GPIO.output(humidifier.pin, humidifier.relay_state)
  humidifier.influx_relay_output()


def fridge_on():
  humidifier.set_override(1)
  humidifier_on()
  fridge.stall_timer_create()
  fridge.stall_timer_update()
  stall_timer = fridge.stall_stop - fridge.stallStart
  while (stall_timer.total_seconds() < config.fridge_stall):
    print 'Running Humidifier for %d seconds before turning on Fridge*********' % config.fridge_stall
    print 'Stall timer = %.1f' % stall_timer.total_seconds()
    time.sleep(5)
    fridge.stall_timer_update()
    stall_timer = fridge.stall_stop - fridge.stallStart
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


def fridge_cycle_on():
  if hasattr(fridge, 'start_timer'):
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
  if hasattr(fridge, 'start_timer'):
    fridge.update_timer()
    fridge_timer = fridge.stop_timer - fridge.start_timer
    print "Fridge Cycle Timer------------%d" % (fridge_timer.total_seconds())
    if (fridge_timer.total_seconds() > config.fridge_cycle) and (fridge.relay_state == 1):
      print "Fridge has been on long enough!!!!!!!!!!!!!!!!!"
      fridge_off()
      print "Fridge turning off!"
  else:
    fridge_off()


def relay_adjustments():
  #Temperature (Fridge and heater).
  if sensor.temperature > (config.desired_temperature + config.drift_temperature):
    fridge_cycle_on()
    heater_off()
  elif sensor.temperature < (config.desired_temperature - config.drift_temperature):
    fridge_cycle_off()
    heater_on()
  elif (config.desired_temperature - config.drift_temperature) <= sensor.temperature <= (config.desired_temperature + config.drift_temperature):
    fridge_cycle_off()
    heater_off()
    print "Temperature is within range!"
  else:
    print "There is a disturbance in the force"

  #Humidity (Humidifier and dehumidifier).
  if sensor.humidity is not None and sensor.humidity < 105:
    if sensor.humidity > (config.desired_humidity + config.drift_humidity):
      if fridge.relay_state == 1: #we always want the humidifier on if the fridge is on.
        humidifier_on()
        dehumidifier_off()
      elif (fridge.relay_state == 0) and (humidifier.override != 1): #don't turn off the humidifier if the override is on.
        humidifier_off()
        dehumidifier_on()
    elif sensor.humidity < (config.desired_humidity - config.drift_humidity):
      humidifier_on()
      dehumidifier_off()
    elif ((config.desired_humidity - config.drift_humidity) <= sensor.humidity <= (config.desired_humidity + config.drift_humidity)) and (humidifier.override != 1):
      humidifier_off()
      dehumidifier_off()
      print "Humidity is within range!"
    else:
      print "There is a disturbance in the force"

