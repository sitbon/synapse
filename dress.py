import cmd
import thinkgear
import subprocess 
import sys

from time import sleep
from nbstreamreader import NonBlockingStreamReader 

from edi2c import pca9685
pwm = pca9685.PCA9685()

class Dress(cmd.Cmd):
    EXERCISE = '0'
    PORTRAY = '1'
    EMBODY = '2'
    SPECULATE = '3'
    MUSE = '4'
    NEVERMIND = '5'
    INVALID = '-1'
    
    pin_demo_switch = '2'
    
    # subprocesses for each sensor interface used in dress
    sp_voice = ""
    sp_mindwave = ""
    sp_heartrate = ""
    sp_proximity = ""
    sp_demo_lights = None

    # instances of nbstreamreader for every subprocess
    # used to communicate with subprocess
    nbsr_voice = ""
    nbsr_mindwave = ""
    nbsr_heartrate = ""
    nbsr_proximity = ""

    is_proximity_active = False
    is_mindwave_active = False
    last_voice_command = ""
    
    def speculate(self):
        print 'turning proximity sensor on'
   	self.is_proximity_active = True
 
    def muse(self):
        print 'turning mindwave on'
	self.is_mindwave_active = False

    def deactivate(self):
        if self.last_voice_command == self.SPECULATE:
	    #led_pattern_command_accepted()
	    self.is_proximity_running = False	
	    self.nbsr_proximity = ''	
            self.sp_proximity.terminate()
	elif self.last_voice_command == self.MUSE:
            #led_pattern_command_accepted()
	    self.is_mindwave_running = False	
	    self.nbsr_mindwvae = ''
	    self.sp_mindwave.terminate()
	else:
	    print ''
  	    #led_pattern_command_rejected()
 
    def deactivate_proximity():
        print 'deactivate proximity - stop interpreting proximity data using lights' 	
    	self.is_proximity_active = False

    def deactivate_mindwave():
        print 'deactivate mindwave - stop interpreting mindwave data using lights'
	self.is_mindwave_active = False

    def led_pattern_command_accepted():
	print 'activate light pattern command accepted'

    def led_pattern_command_rejected():
        print 'activate light pattern command rejected -- invalid command'

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

    def do_monitor(self, line):
	"""Monitors all sensors"""
	lights_are_on = False
        previous_button_value = 1 
	button_down_value = 0
        button_up_value = 1
	while True:
	    demo_button_output = self.read_demo_switch()
	    try:
	        demo_button_output = int(demo_button_output)
	    except:
	        demo_button_output = 0

	    print int(demo_button_output)
            if previous_button_value == int(demo_button_output):
	        print 'do nothing'
	    else:
		if int(demo_button_output) == button_up_value:
		    self.demo_switch_lights()
	    previous_button_value = int(demo_button_output)
	    #self.sp_voice.stdin.write('\n')
	    #voice_output = self.nbsr_voice.readline(0.1)
	    #self.sp_mindwave.stdin.write('\n')	
            #mindwave_output = self.nbsr_mindwave.readline(0.1)
	    #self.sp_mindwave.stdin.write('\n')
            #heartrate_output = self.nbsr_heartrate.readline(0.1)   
	    '''
	    if voice_output:
	        print voice_output
		if self.EXERCISE in voice_output:
		    print 'EXERCISE -- voice command - Testing Stage'
		elif self.PORTRAY in voice_output:
		    print 'PORTRAY -- Picture Mode ON - timeout 10 sec automatically'
		    print 'Phillip/Karli Picture Mode Light Pattern' 
		elif self.EMBODY in voice_output:
		    print 'EMBODY -- Animation Mode ON - Timeout 10 sec automatically'
		    print 'Phillip/Karli Animation Mode Light Pattern'
		elif self.SPECULATE in voice_output:
		    if not self.is_proximity_active:
		    	print 'Start python script to drive light pattern based on proximity data'
		    	self.do_start_proximity(line)
			self.is_proximity_active = True
			self.last_voice_command = self.SPECULATE
		elif self.MUSE in voice_output:
		    self.is_mindwave_active = True
		    print 'Start python script to drive light pattern based on mindwave data'	
		    self.do_start_mindwave(line)
		    self.last_voice_command = self.MUSE
		elif self.NEVERMIND in voice_output:
		    self.deactivate()
		    print 'NEVERMIND - Previously activated sensor deactivated.' 
	    '''
 
	    #if mindwave_output:
	    #	if self.is_mindwave_active:
	    #	    # Add logic for signaling with lights
	    #	    print mindwave_output		
	    #if heartrate_output:
	    #	try:
	    #	   # Add logic for what to do with heart rate
	    #	    print int("0x" + heartrate_output[-4:], 16)
	    # 	except TypeError:
	    #	    print ""			   	
if __name__ == '__main__':
    pin_demo_switch = '2'

    sp_demo_switch = subprocess.Popen(['../GPIO/init_DIG.sh', '-o', pin_demo_switch, '-d', 'input' ],
                                             stdin = subprocess.PIPE,
                                             stdout = subprocess.PIPE,
                                             stderr = subprocess.PIPE, shell = False)
    output = sp_demo_switch.stdout.readline()
    print output

    Dress().do_start_easyvr('')
    sleep(1)
    Dress().do_monitor('')    
    Dress().cmdloop()
         
