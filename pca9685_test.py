from time import time
import sys

from edi2c import pca9685

max_value = int(4096 * .9 * .5)
steps = int(1 + max_value / 16.)


def main_no_program(args):
    dev = pca9685.PCA9685()
    dev.reset(totem=False)

    program = [[0]*steps for _ in range(16)]

    # compress the range of 0-full from N/16 to 1 scaled to steps
    # 0 if step/steps < N/16
    # (steps - (N/16)*steps (1 - N/16)
    for channel in range(16):
        channel_scaled = channel / 16.
        for step in range(steps):
            step_scaled = step / float(steps - 1)
            if step_scaled >= channel_scaled:
                program[channel][step] = int(round(4096 * (step_scaled - channel_scaled) / (1 - channel_scaled)))

    while True:
        elapsed = time()
        for step in range(steps):
            for channel in range(16):
                dev.set_off(channel, program[channel][step])

        for step in reversed(range(steps)):
            for channel in range(16):
                dev.set_off(channel, program[channel][step])

        elapsed = time() - elapsed
        elapsed_per_call = elapsed / (2 * 16 * steps)
        elapsed_per_call_ms = 1000 * round(elapsed_per_call, 6)
        elapsed_ms = 1000 * round(elapsed, 3)
        print elapsed_per_call_ms, "ms/call\t", elapsed_ms, "ms total"

        #pca9685_pwm_config(bus, args.device, 0, 1, 1)


def main(args):
    dev = pca9685.PCA9685()
    dev.reset(totem=False)

    program = [[0.005, [[c, 0, 0] for c in range(pca9685.CHANNELS)]] for _ in range(steps)]

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
    while True:
        main(args)
    sys.exit(0)