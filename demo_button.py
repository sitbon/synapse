#!/usr/bin/env python 
from edi2c import ads1x15

adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)

value = adc.read_single_ended(3)

if value > 3000:
    print 1
else:
    print 0
