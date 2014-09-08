import sys
from edi2c import pca9685 

CHANNELS = pca9685.CHANNELS
MAX_VALUE = pca9685.PWM_MAX_OFF

pwm = pca9685.PCA9685()

def led_portray(args):
    HIGH = MAX_VALUE
    LOW = int(HIGH * .333)
    MEDIUM = int(HIGH * .666)
    PULSE_INTERVAL = 1.0
    RESOLUTION = 4
    
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

    pulse_series_program = generate_pulse(LOW, 0.8)
    pulse_series_program += generate_pulse(MEDIUM, 1.0)
    pulse_series_program += generate_pulse(HIGH, 1.2)

    program = pulse_series_program + [[2, [[None, 0, 0]]]]
    program *= 4

    pwm.run_program(program, debug=False)


def led_pulse(args):
    HIGH = MAX_VALUE
    LOW = int(HIGH * .333)
    MEDIUM = int(HIGH * .666)
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

    pulse_series_program = generate_pulse(HIGH, 1)

    program = pulse_series_program

    while True:
        pwm.run_program(program, debug=False)


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


programs = {
        "portray": led_portray,
        "pulse": led_pulse,
        "proximity_simulation": led_proximity_simulation
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
