import cmd
import thinkgear
import subprocess 
import sys

from time import sleep
from nbstreamreader import NonBlockingStreamReader 
#from pysqlite2 import dbapi2 as sqlite3

from edi2c import pca9685
pwm = pca9685.PCA9685()

# Words to listen for from easyvr.py
EXERCISE = '0'
PORTRAY = '1'
EMBODY = '2'
SPECULATE = '3'
MUSE = '4'
NEVERMIND = '5'
INVALID = '-1'

class Dress(cmd.Cmd):
    pin_demo_switch = '2'
    
    # subprocesses for each sensor interface used in dress
    sp_voice = None 
    sp_mindwave = None 
    sp_heartrate = None 
    sp_proximity = None 
    sp_demo_lights = None

    # instances of nbstreamreader for every subprocess
    # used to communicate with subprocess
    nbsr_voice = None 
    nbsr_mindwave = None 
    nbsr_heartrate = None 
    nbsr_proximity = None 


    def do_EOF(self, line):
       return True

    def do_start_heartrate(self, line):
	self.sp_heartrate = subprocess.Popen(['./gatttool', '-t', 'random', '-b', 'D4:48:C2:4C:A0:19', '-I'],
					stdin=subprocess.PIPE, 
					stdout=subprocess.PIPE,
					stderr = subprocess.PIPE, shell = False)
	self.nbsr_heartrate = NonBlockingStreamReader(self.sp_heartrate.stdout)
	print self.nbsr_heartrate.readline(0.1)	
	self.sp_heartrate.stdin.write('\n')
	self.sp_heartrate.stdin.write('connect')
	self.sp_heartrate.stdin.write('\n')
	sleep(2)
	self.nbsr_heartrate.readline(0.1)
	self.sp_heartrate.stdin.write('char-write-req 18 0100')
	self.sp_heartrate.stdin.write('\n')
	sleep(2)
	print self.nbsr_heartrate.readline(0.1)
	self.sp_heartrate.stdin.write('\n')
	print self.nbsr_heartrate.readline(0.1)
	print self.nbsr_heartrate.readline(0.1)
	print self.nbsr_heartrate.readline(0.1)
	sleep(2)

    def do_start_mindwave(self, line):
	"""starts listening for attention value"""
        self.sp_mindwave = subprocess.Popen(["python", "attention.py"], 
				       stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
				       stderr = subprocess.PIPE, shell = False)
	self.nbsr_mindwave = NonBlockingStreamReader(self.sp_mindwave.stdout)
	self.sp_mindwave.stdin.write('\n')

    def do_start_easyvr(self, line):
	"""starts listening for voice commands"""
	print 'Starting EasyVR'
	self.sp_voice = subprocess.Popen(['python', 'easyvr.py'],
        				 stdin = subprocess.PIPE, 
					 stdout = subprocess.PIPE, 
					 stderr = subprocess.PIPE, shell = False)
	self.nbsr_voice = NonBlockingStreamReader(self.sp_voice.stdout)	
	self.sp_voice.stdin.write('\n')

    def do_start_proximity(self, line):
	"""starts tracking people using proximity"""
	self.sp_proximity = subprocess.Popen(['python', 'mb1200_analog_test.py'],
					     stdin = subprocess.PIPE,
					     stdout = subprocess.PIPE, 
					     stderr = subprocess.PIPE, shell = False)
        self.nbsr_proximity = NonBlockingStreamReader(self.sp_proximity.stdout)
	self.sp_proximity.stdin.write('\n')

    def read_demo_switch(self):
         sp_demo_switch = subprocess.Popen(['./demo_button.py'],
					     stdin = subprocess.PIPE,                                                                                                           
                                             stdout = subprocess.PIPE,                                                                                                          
                                             stderr = subprocess.PIPE, shell = False)
	 return sp_demo_switch.stdout.readline()         

    def demo_switch_lights(self):
	if self.sp_demo_lights is not None and self.sp_demo_lights.poll() is None:
	    print 'Lights on -- turning off'
	    self.sp_demo_lights.terminate()
	    self.sp_demo_lights = None
	    pwm.reset()
	    pwm.set_off(None, 0)
	    return

	self.sp_demo_lights = subprocess.Popen(['python', 'led.py', 
'portray'],
					    stdin = subprocess.PIPE,
					    stdout = subprocess.PIPE,
					    stderr = subprocess.PIPE, shell = False)

    def activate_lights(self, pattern):
        led_arg = None
        if pattern is PORTRAY:
            led_arg = 'portray'
        elif pattern is MUSE:
            led_arg = 'mindwave'
        elif pattern is SPECULATE:
            led_arg = 'proximity'
        else:
            #default is ekg lights
            led_arg = 'ekg'

        sp_lights = subprocess.Popen(['python', 'led.py', led_arg],                         
                                                stdin = subprocess.PIPE,                                
                                                stdout = subprocess.PIPE,                               
                                                stderr = subprocess.PIPE, shell = False)
        return sp_lights

    def do_monitor(self, line):
	"""Monitors all sensors"""
        #open connection to database for web server
        #db = sqlite3.connect('web_server/./dress.db') 
        #c = db.cursor()                                                                                      
        
        led_lights = self.activate_lights('ekg')

        while True:
            if self.sp_voice is not None:
                try:
                    voice_output = self.nbsr_voice.readline(0.1).strip()
                    if voice_output is EXERCISE:
                        print 'activate exercise lights routine'
                    elif voice_output is PORTRAY:
                        print 'activate portray lights routine'
                    elif voice_output is SPECULATE:
                        print 'activate speculate lights routine'
                    elif voice_output is MUSE:
                        print 'activate muse lights routine'
                    elif voice_output is NEVERMIND:
                        print 'canceling lights for previous command'
                except AttributeError:
                    pass 

            if self.sp_heartrate is not None:
                heartrate_output = self.nbsr_heartrate.readline(0.1)   
                self.sp_heartrate.stdin.write('\n')
                if heartrate_output:
       	            try:
	                # Add logic for what to do with heart rate
	                heartrate = int("0x" + heartrate_output[-4:], 16)
                        #c.execute("INSERT INTO heartrate (value) VALUES (?)", (heartrate,))
                        #self.write_heartrate(str(heartrate).strip())
		        led_lights.stdin.write(str(heartrate).strip() + '\n')
                        print heartrate 
	            except TypeError:
	                pass 
            
            if self.sp_proximity is not None:
                 proximity_output = self.nbsr_proximity.readline(0.1)
                 #c.execute("INSERT INTO proximity (value) VALUES (?)", (proximity_output.strip(),))
                 print proximity_output
 
            if self.sp_mindwave is not None:            
                 mindwave_output = self.nbsr_mindwave.readline(0.1)
                 #c.execute("INSERT INTO attention (value) VALUES (?)", (mindwave_output.strip(),))
                 print mindwave_output  

        #c.close()             
if __name__ == '__main__':
    Dress().cmdloop()
