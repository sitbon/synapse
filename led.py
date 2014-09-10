import sys
from edi2c import ads1x15
from edi2c import pca9685 

CHANNELS = pca9685.CHANNELS
MAX_VALUE = pca9685.PWM_MAX_OFF

adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)
pwm = pca9685.PCA9685()

ALL_CHANNELS = None

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
            program_step = [duration, [[channel, 0, index]]]
            pulse_program.append(program_step)
            index += RESOLUTION
        return pulse_program + list(reversed(pulse_program))[1:]

    #pulse_series_program = generate_pulse(LOW, 0.8)
    #pulse_series_program += generate_pulse(MEDIUM, 1.0)
    #pulse_series_program += generate_pulse(HIGH, 1.2)

    pulse_series_program = generate_pulse(LOW, 1.6)
    pulse_series_program += generate_pulse(MEDIUM, 2.0)
    pulse_series_program += generate_pulse(HIGH, 2.5)


    program = pulse_series_program + [[2, [[channel, 0, 0]]]]
    program *= 4

    pwm.run_program(program, debug=False)


def led_pulse(amplitude=MAX_VALUE):
    PULSE_INTERVAL = 1.0
    RESOLUTION = int(MAX_VALUE * .15)
    
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
                program[step][1][channel] = channel, 0, int(round(MAX_VALUE * (step_scaled - channel_scaled) / (1 - channel_scaled)))

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
        "proximity_simulation": led_proximity_simulation_sequenced,
        "proximity": led_proximity,
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

if __name__ == '__main__':
    if len(sys.argv) <= 1:
        usage()
    else:
        args = sys.argv[1:]
        name = args[0]
        run_program(name, args[1:])
