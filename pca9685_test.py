from time import time
import sys

from edi2c import pca9685

max_value = 40 #int(4096 * .9 * .5)
steps = int(1 + max_value / 2.)
channel_scale_factor = 16

def main(args):
    dev = pca9685.PCA9685()
    dev.reset(frequency=1500)

    program = [[0.025, [[c, 0, 0] for c in range(pca9685.CHANNELS)]] for _ in range(steps)]

    # compress the range of 0-full from N/16 to 1 scaled to steps
    # 0 if step/steps < N/16
    # (steps - (N/16)*steps (1 - N/16)
    for channel in range(16):
        channel_scaled = channel / 16.
        for step in range(steps):
            step_scaled = step / float(steps - 1)
            if step_scaled >= channel_scaled:
                program[step][1][channel] = channel, 0, int(round(max_value * (step_scaled - channel_scaled) / (1 - channel_scaled)))

    while True:
        dev.run_program(program, debug=True)
        dev.run_program(reversed(program), debug=True)

if __name__ == '__main__':
    args = sys.argv[1:]
    main(args)
    sys.exit(0)