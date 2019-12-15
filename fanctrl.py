#!/usr/bin/env python3
# -*- coding: utf8 -*-
import sys
import time
import argparse
import RPi.GPIO as GPIO
from time import gmtime, strftime
from apscheduler.schedulers.blocking import BlockingScheduler

FAN_PIN = 17 # Real pin number: 11
TEMPERATURE_TRIGGER = 30 # Triggers fan when this temperature (C°) is exceeded
TIMER_MIN = 5 
INTERVAL_MIN = 10
FORCE_DEFAULT = 15
INTERVAL_DEFAULT = 30

scheduler = BlockingScheduler()

def gpio_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(FAN_PIN, GPIO.OUT)

def gpio_destroy():
    GPIO.output(FAN_PIN, GPIO.LOW)
    GPIO.cleanup()

def run(timer:int):
    GPIO.output(FAN_PIN, GPIO.HIGH)
    time.sleep(timer)
    GPIO.output(FAN_PIN, GPIO.LOW)

def write_log(log_str:str, log_file=None):
    if log_file is None:
        print(log_str, end='', flush=True)
    else:
        log_file.write(log_str)

def log_pre(timer:int, temperature:int, log_file=None):
    time_ = strftime('%Y-%m-%d %H:%M:%S', gmtime())
    log_str = '{} + {}s: {}°C'.format(time_, timer, temperature)
    write_log(log_str, log_file)

def log_suf(temperature:int, log_file=None):
    log_str = ' -> {}°C\n'.format(temperature)
    write_log(log_str, log_file)

def temperature2timer(temperature:int, interval:int):
    timer = max(TIMER_MIN, int(temperature))
    timer = min(temperature, interval-2)
    return timer

def schedule(interval:int, log_file=None):
    def scheduler_callback():
        temperature = cpu_temperature()
        if temperature > TEMPERATURE_TRIGGER:
            timer = temperature2timer(temperature, interval)
            log_pre(timer, temperature, log_file)
            run(timer=timer)
            log_suf(cpu_temperature(), log_file)
    scheduler.add_job(scheduler_callback, 'interval', seconds=interval,
            replace_existing=True)
    scheduler.start()

def cpu_temperature() -> float:
    with open('/sys/class/thermal/thermal_zone0/temp') as cpu_file:
        cpu_temp = cpu_file.read()
    return float(cpu_temp)/1000

def parse_args():
    def check_min(value, min_value:int):
        ivalue = int(value)
        if ivalue < min_value:
            raise argparse.ArgumentTypeError("""Interval is {} but must be \
>= {}""".format(value, min_value))
        return ivalue

    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--force', nargs='?', help="""Force fan on for \
            FORCE time (default: {}s), no matter the temperature, and quit. \
            Program does not enter scheduling mode and ignores any other \
            flags.""".format(FORCE_DEFAULT),
            type=lambda value:(check_min(value, 0)), const=15)

    parser.add_argument('-i','--interval', nargs='?', help="""Interval in \
which cpu temperature is checked. Min: {}s, Default:
{}s""".format(INTERVAL_MIN, INTERVAL_DEFAULT),
type=lambda value:(check_min(value, INTERVAL_MIN)), default=INTERVAL_DEFAULT)

    parser.add_argument('-l','--log', nargs='?', help="""Log file \
temperature changes are written to. Called once in an interval""",type=str)

    return parser.parse_args()

def main():
    try:
        gpio_setup()
        args = parse_args()
        log_file = None
        if args.log:
            log_file = open(args.log, 'a', buffering=1)
        if args.force:
            temperature = cpu_temperature()
            log_pre(timer=args.force, temperature=temperature, log_file=log_file)
            try:
                run(timer=args.force)
            except KeyboardInterrupt:
                log_suf(temperature=cpu_temperature(), log_file=log_file)
                raise
            log_suf(temperature=cpu_temperature(), log_file=log_file)
        else:
            try:
                schedule(interval=args.interval, log_file=log_file)
            except KeyboardInterrupt:
                scheduler.shutdown()
                raise
        if log_file is not None:
            log_file.close()
        gpio_destroy()
    except KeyboardInterrupt:
        gpio_destroy()
        sys.exit(1)

if __name__ == '__main__':
    main()
