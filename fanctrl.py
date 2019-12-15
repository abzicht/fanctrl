#!/usr/bin/env python3
# -*- coding: utf8 -*-
import sys
import time
import argparse
import RPi.GPIO as GPIO
from time import gmtime, strftime
from apscheduler.schedulers.blocking import BlockingScheduler

# Real pin number: 11
FAN_PIN_DEFAULT = 17 
# Default temperature (°C) at which scheduled job triggers fan
TEMPERATURE_TRIGGER_DEFAULT = 48 
# Minimum time for cooling procedure
TIMER_MIN = 5
# Minimum interval for scheduler
INTERVAL_MIN = 10
# Default interval for scheduler
INTERVAL_DEFAULT = 30
# Default time for cooling procedure in force mode
FORCE_DEFAULT = 15

scheduler = BlockingScheduler()

def gpio_setup(fan_pin:int):
    """
    Sets up GPIOs the clean way
    """
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(fan_pin, GPIO.OUT)

def gpio_destroy(fan_pin:int):
    """
    Destroys any GPIO reservations (Exiting the clean way).
    """
    GPIO.output(fan_pin, GPIO.LOW)
    GPIO.cleanup()

def run(timer:int, fan_pin:int):
    """
    Pulls 'fan_pin' to LOW for 'timer' time.
    Blocking
    """
    GPIO.output(fan_pin, GPIO.HIGH)
    time.sleep(timer)
    GPIO.output(fan_pin, GPIO.LOW)

def write_log(log_str:str, log_file=None):
    """
    Writes 'log_str' to 'log_file'. If 'log_file' is None, content is written
    to sys.stdout
    """
    if log_file is None:
        print(log_str, end='', flush=True)
    else:
        log_file.write(log_str)

def log_pre(timer:int, temperature:int, log_file=None):
    """
    Log line prefix. Typically looking like this:
    '2019-12-15 19:33:10 + 8s: 39.166°C'
    """
    time_ = strftime('%Y-%m-%d %H:%M:%S', gmtime())
    log_str = '{} + {}s: {}°C'.format(time_, timer, temperature)
    write_log(log_str, log_file)

def log_suf(temperature:int, log_file=None):
    """
    Log line suffix. Typically looking like this:
    ' -> 38.628°C
    """
    log_str = ' -> {}°C\n'.format(temperature)
    write_log(log_str, log_file)

def temperature2timer(temperature:int, interval:int):
    """
    Determines the cooling length. Put your fancy AI functions here
    """
    timer = max(TIMER_MIN, int(temperature/2))
    timer = min(temperature, interval-2)
    return timer

def schedule(interval:int, min_temperature:int, fan_pin:int, log_file=None):
    """
    Blocking scheduler for cooling whenever it is necessary
    """
    def scheduler_callback():
        temperature = cpu_temperature()
        if temperature > min_temperature:
            timer = temperature2timer(temperature, interval)
            log_pre(timer, temperature, log_file)
            run(timer=timer, fan_pin=fan_pin)
            log_suf(cpu_temperature(), log_file)

    scheduler.add_job(scheduler_callback, 'interval', seconds=interval,
            replace_existing=True)
    scheduler.start()

def cpu_temperature() -> float:
    """
    Determines the cpu temperature based on the contents of
    /sys/class/thermal/thermal_zone0/temp.
    """
    with open('/sys/class/thermal/thermal_zone0/temp') as cpu_file:
        cpu_temp = cpu_file.read()
    return float(cpu_temp)/1000

def parse_args():
    """
    Parses arguments passed to fanctrl
    """
    def check_min(value, min_value:int):
        ivalue = int(value)
        if ivalue < min_value:
            raise argparse.ArgumentTypeError("""Interval is {} but must be \
>= {}""".format(value, min_value))
        return ivalue

    parser = argparse.ArgumentParser()
    parser.add_argument('-f','--force', nargs='?', help="""Force fan on for \
            FORCE time (default: {}s), no matter the temperature, and quit. \
            Program does not enter scheduling mode.""".format(FORCE_DEFAULT),
            type=lambda value:(check_min(value, 0)), const=15)

    parser.add_argument('-i','--interval', nargs='?', help="""Interval in \
which cpu temperature is checked. Min: {}s, Default: \
{}s""".format(INTERVAL_MIN, INTERVAL_DEFAULT),
        type=lambda value:(check_min(value, INTERVAL_MIN)), default=INTERVAL_DEFAULT)

    parser.add_argument('-t','--temperature', nargs='?', help="""Temperature \
(in °C) at which the cooling function is \
triggered. Default: {}°C""".format(TEMPERATURE_TRIGGER_DEFAULT), type=int,
        default=TEMPERATURE_TRIGGER_DEFAULT)

    parser.add_argument('-p','--pin', nargs='?', help="""Physical pin which
            triggers the fan (BCM mode). Default: {}""".format(FAN_PIN_DEFAULT),
            type=int, default=FAN_PIN_DEFAULT)

    parser.add_argument('-l','--log', nargs='?', help="""The log file \
temperature changes are written to. Called once per interval.""",type=str)

    return parser.parse_args()

def main():
    """
    Fill sys.argv with arguments and run this function
    """
    try:
        args = parse_args()
        gpio_setup(args.pin)
        log_file = None
        if args.log:
            log_file = open(args.log, 'a', buffering=1)
        if args.force:
            temperature = cpu_temperature()
            log_pre(timer=args.force, temperature=temperature, log_file=log_file)
            try:
                run(timer=args.force, fan_pin=args.pin)
            except KeyboardInterrupt:
                log_suf(temperature=cpu_temperature(), log_file=log_file)
                raise
            log_suf(temperature=cpu_temperature(), log_file=log_file)
        else:
            try:
                schedule(interval=args.interval, min_temperature=args.temperature,
                    fan_pin=args.pin, log_file=log_file)
            except KeyboardInterrupt:
                scheduler.shutdown()
                raise
        if log_file is not None:
            log_file.close()
        gpio_destroy(args.pin)
    except KeyboardInterrupt:
        gpio_destroy(args.pin)
        sys.exit(1)

if __name__ == '__main__':
    main()
