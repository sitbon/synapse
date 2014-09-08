#!/usr/bin/env python 
import sys, os
from time import sleep
from subprocess import Popen
from edi2c import ads1x15


BUTTON_COMMAND = "python"
BUTTON_SCRIPT = "led.py"
BUTTON_ARGS = ["pulse"]

PATH = os.path.dirname(__file__)

script_path = os.path.join(PATH, BUTTON_SCRIPT)
script_arg = [BUTTON_COMMAND, script_path] + BUTTON_ARGS
process = None

adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)


def main():
    while True:
        try:
            value = adc.read_single_ended(3)

            if value > 3000:
                run_command()
                sleep(0.700)
            else:
                sleep(0.120)
        except Exception, e:
            print >>sys.stderr, "BUTTON:", str(e)
            continue


def run_command():
    global process
    
    if process is None or process.poll() is not None:
        try:
            print >>sys.stderr, "BUTTON:", " ".join(script_arg)
            process = Popen(script_arg)
        except Exception, e:
            print >>sys.stderr, "BUTTON:", str(e)
    else:
        print >>sys.stderr, "BUTTON:", "terminating"
        process.terminate()
        process = None


if __name__ == '__main__':
    main()