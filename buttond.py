#!/usr/bin/env python 
import sys, os, signal
from time import time, sleep
from subprocess import Popen
from edi2c import ads1x15


BUTTON_COMMAND = "python"
BUTTON_SCRIPT = "led.py"
BUTTON_ARGS = ["proximity_simulation"]

BUTTON_LONG_PRESS_COMMAND = "sh"
BUTTON_LONG_PRESS_SCRIPT = "run_attention.sh"
BUTTON_LONG_PRESS_ARGS = [""]

PATH = os.path.dirname(__file__)

script_path = os.path.join(PATH, BUTTON_SCRIPT)
script_arg = [BUTTON_COMMAND, script_path] + BUTTON_ARGS
long_press_script_path = os.path.join(PATH, BUTTON_LONG_PRESS_SCRIPT)
long_press_script_arg = [BUTTON_LONG_PRESS_COMMAND, long_press_script_path] + BUTTON_LONG_PRESS_ARGS

process = None

adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)
down = False
down_time = 0

def main():
    global down
    
    while True:
        try:
            value = adc.read_single_ended(3)

            if value > 3000:
                if not down:
                    down_time = time()
                    down = True

                sleep(0.250)
            else:
                if down:
                    down = False
                    down_time = time() - down_time
                    long_press = False

                    print >>sys.stderr, "BUTTON:", "press time", round(down_time, 2)
                    
                    if down_time >= 0.200:
                        if down_time >= 3.5:
                            long_press = True

                        run_command(long_press)
                        sleep(0.500)
                    elif process is not None and process.poll() is None:
                        print >>sys.stderr, "BUTTON:", "terminating"
                        process.terminate()
                        sleep(0.350)

                sleep(0.075)

        except Exception, e:
            print >>sys.stderr, "BUTTON:", str(e)
            sleep(3)
            continue


def run_command(long_press=False):
    global process
    
    if long_press:
        popen_arg = long_press_script_arg
    else:
        popen_arg = script_arg
    
    if process is None or process.poll() is not None:
        try:
            print >>sys.stderr, "BUTTON:", " ".join(popen_arg)
            process = Popen(popen_arg, preexec_fn=os.setsid)
        except Exception, e:
            print >>sys.stderr, "BUTTON:", str(e)
    else:
        print >>sys.stderr, "BUTTON:", "terminating"
        do_kill(process)
        process = None

def do_kill(process):
    try:
        #process.terminate()
        os.killpg(process.pid, signal.SIGTERM)
    except Exception, e:
        print >>sys.stderr, "BUTTON:", "killing caused error", str(e)

if __name__ == '__main__':
    main()

