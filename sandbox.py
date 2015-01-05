"""Utilities for the interactive interpreter.
""" 
import sys, os
from time import sleep, time
from threading import Thread
from multiprocessing import Process

from edi2c import pca9685, ads1x15, i2c
from edi2c.pca9685 import PCA9685
from edi2c.ads1x15 import ADS1X15
from edi2c.i2c import I2CDevice

pwm = PCA9685()
adc = ADS1X15()

import lights
