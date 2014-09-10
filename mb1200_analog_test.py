import sys

from edi2c import ads1x15
from edi2c import pca9685


def main(args):
    pwm = pca9685.PCA9685()
    pwm.reset()
    adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)

    steps = int(1 + 4096 / 30.)
    program = [[0.000, [[c, 0, 0] for c in range(pca9685.CHANNELS)]] for _ in range(steps)]

    # compress the range of 0-full from N/16 to 1 scaled to steps
    # 0 if step/steps < N/16
    # (steps - (N/16)*steps (1 - N/16)
    for channel in range(16):
        channel_scaled = channel / 16.
        for step in range(steps):
            step_scaled = step / float(steps - 1)
            if step_scaled >= channel_scaled:
                program[step][1][channel] = channel, 0, int(round(4096 * (step_scaled - channel_scaled) / (1 - channel_scaled)))

    program = list(reversed(program))

    readings = []

    median_readings = 15

    while True:
        #vcc = adc.read_single_ended(1, pga=6144, sps=128)
        distance = adc.read_single_ended(0, pga=1024, sps=1600) * 1024 / 3300.
        readings.append(distance)

        # Median filter
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

        on = 1 - min(max(distance - 20, 0) / 110., 1.)
        step = int(round((len(program) - 1) * on))
        print int(round(distance)), "cm" , on
        #pwm.run_program(program[step:step+1])

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
    sys.exit(0)