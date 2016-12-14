#!/usr/bin/python
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

number = 17
GPIO.setup(number,GPIO.OUT)
GPIO.output(number,GPIO.HIGH)

sleeptm = .25
try:
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.LOW)
  time.sleep(sleeptm);
  GPIO.output(number, GPIO.HIGH)
  GPIO.cleanup()

except KeyboardInterrupt:
  GPIO.cleanup()
