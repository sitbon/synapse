""" Notifies when button is clicked
"""
from multiprocessing import Process
from edi2c import ads1x15
from time import sleep

DEBUG = False

class Button():
    adc = None
    channel = None
    

    def __init__(self, channel=1):
         self.adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)
         self.channel = channel
       
    def _monitor_button(self, callback):
        already_down = False                                                   
                                                    
        while True:                                 
            sleep(0.100)
            if self.adc.read_single_ended(self.channel) < 1000:     
                down = True                         
                if not already_down:                
                    if not callback():
                        return
                already_down = True                 
            else:                                   
                already_down = False 

    def monitor_button(self, callback):
        Process(target=self._monitor_button, args=(callback,)).start()

def update():
    print 'toggled!'
    return True

if __name__ == '__main__':
    button = Button()
    button.monitor_button(update)
    while True:
        sleep(0.100)
