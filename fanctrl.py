#!/usr/bin/env python3
# -*- coding: utf8 -*-
import RPi.GPIO as GPIO
import time
from time import gmtime, strftime
import sys

FAN_PIN = 17 # Real pin number: 11
TRIGGER = 48 # Triggers fan when this temperature (C°) is exceeded
ON_TIME = 59 # The duration the fan is run (s)

def cpu_temperature() -> float:
    tempFile = open('/sys/class/thermal/thermal_zone0/temp')
    cpu_temp = tempFile.read()
    tempFile.close()
    return float(cpu_temp)/1000


def run(t):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)
    GPIO.output(FAN_PIN, GPIO.HIGH)
    time.sleep(t)
    GPIO.output(FAN_PIN, GPIO.LOW)

def destroy():
    GPIO.output(FAN_PIN, GPIO.LOW)
    GPIO.cleanup()

def is_forced() -> bool:
    return (len(sys.argv)>1 and sys.argv[1]=='-f') or (len(sys.argv)>2 and sys.argv[2]=='-f')

def stats_file() -> str:
    if len(sys.argv)>1 and sys.argv[1]!='-f':
        return sys.argv[1]
    return None

def write_to_file(temp, filepath):
    time_ = strftime('%Y-%m-%d %H:%M:%S', gmtime())
    with open(filepath, 'a') as file_:
        file_.write(time_ + ': ' + str(temp) + '°C' + (' forced' if is_forced() else '') +'\n')

if __name__ == '__main__':
    temp = cpu_temperature()
    if temp>TRIGGER or is_forced():
        try:
            filepath = stats_file()
            if filepath is not None:
                write_to_file(temp, filepath)
            run(ON_TIME)
            destroy()
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program
            destroy()              # destroy() is executed to clean up pin reservations.
            sys.exit(1)
        print(str(temp) + ' -> ' + str(cpu_temperature()))
    else:
        print(temp)
    sys.exit(0)
