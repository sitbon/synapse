import sys, threading
from time import sleep
from edi2c import ads1x15
from edi2c import pca9685 

CHANNELS = pca9685.CHANNELS
MAX_VALUE = pca9685.PWM_MAX_OFF
ALL_CHANNELS = None

MAP = [1, 4, 5, 0, 3, 2, 6, 7, 10, 13, 8, 9, 11, 12, 14, 15]

LEVELS = [
    [0],
    [1, 2],
    [3, 4, 5],
    [6, 7],
    [8, 9],
    [10, 11, 12, 13]
]

adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)
pwm = pca9685.PCA9685()

ekg_bpm = 60

def ekg_task():
    global ekg_bpm
    print >>sys.stderr, "LIGHTS: EKG read stdin running"
    try:
        while True:
            print >>sys.stderr, "LIGHTS: waiting for EKG input"
            value = sys.stdin.readline()
            print >>sys.stderr, "LIGHTS: value =", repr(value)
            ekg_bpm = int(value)
            continue

            value = value.strip()

            try:
                print >>sys.stderr, "LIGHTS: parsing value"
                #value = int(value)
                value = 60
            except:
                print >>sys.stderr, "LIGHTS: bad value", value
                continue

        print >>sys.stderr, "LIGHTS: setting BPM"
        ekg_bpm = value
        print >>sys.stderr, "LIGHTS: EKG at", ekg_bpm, "BPM"
    except Exception, e:
        print >>sys.stderr, "LIGHTS:", str(e)
    finally:
        print >>sys.stderr, "LIGHTS: EKG task exiting"


def led_ekg(args):
    intensity_map = lambda x: max(0.0, float(x - 50) / (90.0 - 50.0))
    
    

    def ekg_led_task():
        print >>sys.stderr, "LIGHTS: EKG lights running"
        program = []
    
        step_duration = lambda: (60.0 / float(ekg_bpm)) / float(len(program))
        
        for level in LEVELS:
            activations = [[MAP[c], 0, 30] for c in level]
            for level2 in LEVELS:
                if level2 != level:
                    activations += [[MAP[c], 0, 0] for c in level2]

            on = [step_duration, activations]
            #off = [0, [[MAP[c], 0, 0] for c in level]]
            program.append(on)
            
        program += list(reversed(program))[1:]

        while True:
            pwm.run_program(program, debug=False)

    ekg_thread = threading.Thread(target=ekg_led_task)
    ekg_thread.setDaemon(True)
    ekg_thread.start()
    sleep(0.001)

    ekg_task()


def led_mindwave(args):
    intensity_map = lambda x: max(0.0, float(x - 50) / (90.0 - 50.0))
    
    program = []
    
    for level in LEVELS:
        on = [0, [[MAP[c], 0, 16] for c in level]]
        #off = [0, [[MAP[c], 0, 0] for c in level]]
        program.append(on)
        
    while True:
        value = sys.stdin.readline()
        value = value.strip()

        try:
            value = int(value)
        except:
            continue

        on = intensity_map(value)
        step = min(len(program) - 1, max(0, int(round((len(program) - 1) * on))))
        print "LIGHTS:", str(round(on * 100)) + "%", program[step:step+1]
        pwm.set_off(None, 0)
        pwm.run_program(program[:step+1])


def led_climb_test(args):
    duration = 5.0
    program = []
    
    for level in LEVELS:
        on = [duration / float(len(LEVELS)), [[MAP[c], 0, 3] for c in level]]
        #off = [0, [[MAP[c], 0, 0] for c in level]]
        program.append(on)

    pwm.run_program(program, debug=False)

def led_map_assist(args):
    duration = 5.0
    program = []

    for channel in range(CHANNELS):
        program.append([duration, [[channel, 0, 10]]])
        program.append([0, [[channel, 0, 0]]])

    pwm.run_program(program, debug=False)


def led_portray(args):
    HIGH = MAX_VALUE
    LOW = int(HIGH * .333)
    MEDIUM = int(HIGH * .666)
    PULSE_INTERVAL = 2.0
    RESOLUTION = max(1, int(MAX_VALUE * .01))
    channel = ALL_CHANNELS
    
    def generate_pulse(peak, pulse_interval=PULSE_INTERVAL, duration_at=None):
        index = 0
        pulse_program = []
        while index <= peak:
            if duration_at is None:
                duration = pulse_interval / ((2. * peak + 1) / RESOLUTION)
            else:
                duration = duration_at(index)
            value = index
            program_step = [duration, [[MAP[channel], 0, index]]]
            pulse_program.append(program_step)
            index += RESOLUTION
        return pulse_program + list(reversed(pulse_program))[1:]

    #pulse_series_program = generate_pulse(LOW, 0.8)
    #pulse_series_program += generate_pulse(MEDIUM, 1.0)
    #pulse_series_program += generate_pulse(HIGH, 1.2)

    pulse_series_program = generate_pulse(LOW, 1.6)
    pulse_series_program += generate_pulse(MEDIUM, 2.0)
    pulse_series_program += generate_pulse(HIGH, 2.5)


    program = pulse_series_program + [[2, [[MAP[channel], 0, 0]]]]
    program *= 4

    pwm.run_program(program, debug=False)


def led_pulse(args):
    amplitude = 8
    PULSE_INTERVAL = 1.0
    RESOLUTION = 1
    
    def generate_pulse(peak, pulse_interval=PULSE_INTERVAL, duration_at=None):
        index = 0
        pulse_program = []
        while index <= peak:
            if duration_at is None:
                duration = pulse_interval / ((2. * peak + 1) / RESOLUTION)
            else:
                duration = duration_at(index)
            value = index
            program_step = [duration, [[None, 0, index]]]
            pulse_program.append(program_step)
            index += RESOLUTION
        return pulse_program + list(reversed(pulse_program))[1:]

    pulse_series_program = generate_pulse(amplitude, 1.5)

    program = pulse_series_program

    while True:
        pwm.run_program(program, debug=False)



def led_pulse_fast(args):
    amplitude = 8
    PULSE_INTERVAL = 0.5
    RESOLUTION = 1
    
    def generate_pulse(peak, pulse_interval=PULSE_INTERVAL, duration_at=None):
        index = 0
        pulse_program = []
        while index <= peak:
            if duration_at is None:
                duration = pulse_interval / ((2. * peak + 1) / RESOLUTION)
            else:
                duration = duration_at(index)
            value = index
            program_step = [duration, [[None, 0, index]]]
            pulse_program.append(program_step)
            index += RESOLUTION
        return pulse_program + list(reversed(pulse_program))[1:]

    pulse_series_program = generate_pulse(amplitude, 0.5)

    program = pulse_series_program

    while True:
        pwm.run_program(program, debug=False)


def led_proximity_simulation_sequenced(args):
    HIGH = MAX_VALUE
    LOW = int(HIGH * .10)
    MEDIUM = int(HIGH * .25)
    RAMP_INTERVAL = 1.0
    RESOLUTION = max(1, int(MAX_VALUE * .01))
    
    def generate_ramp(start, peak, ramp_interval=RAMP_INTERVAL, duration_at=None):
        index = start
        ramp_program = []
        while index <= peak:
            if duration_at is None:
                duration = float(ramp_interval) / (((peak - start) + 1) / RESOLUTION)
            else:
                duration = duration_at(index)
            value = index
            program_step = [duration, [[ALL_CHANNELS, 0, index]]]
            ramp_program.append(program_step)
            index += RESOLUTION
        return ramp_program

    ramp_series_program = []
    ramp_series_program += generate_ramp(0, LOW, 2.5)
    ramp_series_program += generate_ramp(LOW+1, MEDIUM, 4)
    ramp_series_program += list(reversed(generate_ramp(0, MEDIUM-1, 1.25)))

    program = ramp_series_program
    pwm.run_program(program, debug=False)
    
    lowr = generate_ramp(0, 13, 1.25)
    lowr += list(reversed(lowr))[1:]
    
    #highr = generate_ramp(0, MEDIUM, 1.25)
    #highr += list(reversed(highr))[1:]
    #pwm.run_program(program, debug=False)
    
    while True:
        pwm.run_program(lowr, debug=False)
    


def led_proximity_simulation(args):
    steps = MAX_VALUE
    length = 2.66
    program = [[(length / 2.0) / steps, [[c, 0, 0] for c in range(CHANNELS)]] for _ in range(steps)]

    # compress the range of 0-full from N/16 to 1 scaled to steps
    # 0 if step/steps < N/16
    # (steps - (N/16)*steps (1 - N/16)
    
    for channel in range(CHANNELS):
        channel_scaled = channel / float(CHANNELS)
        for step in range(steps):
            step_scaled = step / float(steps - 1)
            if step_scaled >= channel_scaled:
                program[step][1][MAP[channel]] = MAP[channel], 0, int(round(MAX_VALUE * (step_scaled - channel_scaled) / (1 - channel_scaled)))

    program += list(reversed(program))[1:]
    pwm.run_program(program, debug=False)


def led_proximity(args):
    # map: on = 1 - min(max(distance - 20, 0) / 130., 1.)
    RAMP_INTERVAL = 0.0
    RESOLUTION = int(MAX_VALUE * .15)
    
    def generate_ramp(peak, ramp_interval=RAMP_INTERVAL, duration_at=None):
        index = 0
        ramp_program = []
        while index <= peak:
            if duration_at is None:
                duration = ramp_interval / ((peak + 1) / RESOLUTION)
            else:
                duration = duration_at(index)
            value = index
            program_step = [duration, [[ALL_CHANNELS, 0, index]]]
            ramp_program.append(program_step)
            index += RESOLUTION
        return ramp_program
    
    program = generate_ramp(MAX_VALUE)
    
    readings = []
    median_readings = 15

    while True:
        #vcc = adc.read_single_ended(1, pga=6144, sps=128)
        distance = adc.read_single_ended(0, pga=1024, sps=1600) * 1024 / 3300.
        readings.append(distance)

        if len(readings) == median_readings:
            readings.sort()
            distance = readings[median_readings/2]
            readings = []
        else:
            continue

        #print int(round(distance)), "cm"  # , int(round(vcc)), "mv"

        #if abs(distance2 - distance) > 40:
        #    print "[reject]"
        #    #distance = 10000
        #    continue
        #else:
        #    distance = (distance + distance2) / 2.
        #    print

        on = 1 - min(max(distance - 20, 0) / 77., 1.)
        step = int(round((len(program) - 1) * on))
        #print int(round(distance)), "cm" , round(on, 2)
        pwm.run_program(program[step:step+1])

programs = {
        "portray": led_portray,
        "pulse": led_pulse,
        "pulse_fast": led_pulse_fast,
        "proximity_simulation": led_proximity_simulation_sequenced,
        "proximity": led_proximity,
        "map_assist": led_map_assist,
        "climb_test": led_climb_test,
        "mindwave": led_mindwave,
        "ekg": led_ekg,
    }


def run_program(name, args):
    program_handler = programs.get(name, None)

    if program_handler is None:
        usage()
    else:
        pwm.reset()

        try:
            program = program_handler(args)
        finally:
            pwm.reset()

def usage():
    print >>sys.stderr, "usage:", sys.argv[0], "<program>"
    print >>sys.stderr, "\n".join(programs.keys())

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        usage()
    else:
        args = sys.argv[1:]
        name = args[0]
        run_program(name, args[1:])
