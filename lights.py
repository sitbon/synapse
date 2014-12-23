import sys, threading
from time import sleep
from edi2c import ads1x15
from edi2c import pca9685 


FREQUENCY = 180
MAX_VALUE = 1000

#MAP = [1, 4, 5, 0, 3, 2, 6, 7, 10, 13, 8, 9, 11, 12, 14, 15]
MAP = [0, 1, 2, 3]

LEVELS = [
    [0],
    [1],
    [2],
    [3],
]

#LEVELS = [
#    [0],
#    [1, 2],
#    [3, 4, 5],
#    [6, 7],
#    [8, 9],
#    [10, 11, 12, 13]
#]

#adc = ads1x15.ADS1X15(ic=ads1x15.IC_ADS1115)

class ProgramBuilder:
    program = None
    activations = None
    duration = 0.0

    def __init__(self):
        self.clear()

    def get(self):
        if len(self.activations) > 0:
            self.step()
            
        return self.program

    def duration(self, duration):
        self.duration = float(duration)
        return self

    def clear(self):
        self.program = []
        self.activations = []
        self.duration = 0.0
        return self

    def add(self, channel, value):
        self.activations.append((channel, value))
        return self

    def step(self, duration=None):
        if duration is not None:
            self.duration = duration
            
        self.program.append((self.duration, self.activations))
        self.duration = 0.0
        self.activations = []
        return self

    def lerp(self, duration=None, resolution=100):
        """Linear interpolation between program state and current activations.
        """
        if duration is None:
            duration = self.duration
        else:
            duration = float(duration)

        if duration <= 0 or resolution <= 1:
            raise ValueError, "Invalid duration/resolution"
        
        if not len(self.program):
            begin = {}
            begin_duration = 0
        else:
            begin = dict(self.program[-1][1])
            begin_duration, begin_activations = self.program.pop()
            
        if not len(self.activations):
            end = {}
        else:
            end = dict(self.activations)

        channels = set(begin.keys() + end.keys())
        t_step = duration / resolution
        
        lerp_program = []
        
        for i in range(resolution + 1):
            p = float(i) / resolution
            t_activations = {}
            
            for channel in channels:
                a1 = begin.get(channel, 0)
                a2 = end.get(channel, 0)
                t_activations[channel] = a1 + (a2 - a1) * p
                
            if i == 0:
                lerp_program.append((begin_duration, t_activations.items()))
            else:
                lerp_program.append((t_step, t_activations.items()))

        self.program.extend(lerp_program)
        self.activations = []
        self.duration = 0.0
        return self
        

class Lights:
    PROGRAM_FULL_ON = ProgramBuilder().add(None, 1.0).get()
    PROGRAM_FULL_OFF = ProgramBuilder().add(None, 0.0).get()
    pwm = None
    debug = False
    
    def __init__(self, debug=False):
        self.debug = debug
        self.pwm = pca9685.PCA9685(debug=debug)
        self.reset()
    
    def reset(self):
        self.pwm.reset(frequency=FREQUENCY)

    def set_all(self, intensity):
        self.run_program(ProgramBuilder().add(None, intensity).get())
        
    def set_all_on(self):
        self.run_program(Lights.PROGRAM_FULL_ON)
        
    def set_all_off(self):
        self.run_program(Lights.PROGRAM_FULL_OFF)

    def run_program(self, program, debug=False):
        """Run a program given as a list of times and activations (float 0->1):
            duration1, [(channel1A, value1A), (channel1B, value1B)]
        
        Alternatively, use the ProgramBuilder:
            ProgramBuilder().add(channel1A, value1A).add(channel1B, value1B).step(duration).get()
        """
        pca_program = []
        
        for duration, activations in program:
            pca_activations = []
            
            for channel, off in activations:
                if off < 0 or off > 1:
                    raise ValueError, "Invalid activation value: must be in [0,1]"
                
                off = int(off * MAX_VALUE)
                
                if channel is None or channel < 0 or channel >= len(MAP):
                    pca_activations.extend((c, 0, off) for c in MAP)
                else:
                    pca_activations.append((MAP[channel], 0, off))
                    
            pca_program.append((duration, pca_activations))

        self.pwm.run_program(pca_program, debug=debug)

class ProximityLights(Lights):
    program_on = None                  
    program_off = None
    builder_on = None
    builder_off = None                                                                                        
    current_space = None
                                   
    def __init__(self, *args, **kwargs):
        Lights.__init__(self, *args, **kwargs)
        self.generate_program()               
                                                                                                               
    def generate_program(self):          
        self.builder_on = ProgramBuilder()     
        self.builder_off = ProgramBuilder()                                                                        

        intensity_on = 0
        intensity_off = 1                                             
        for level in LEVELS:                
             intensity_on = intensity_on + 0.20
             intensity_off = intensity_off - 0.20
             for c in level:                                                                                   
                self.builder_on.add(c, 1)        
                self.builder_off.add(c, 0)
             
             self.builder_on.step()            
             self.builder_off.step()           
                                                                                                              
        self.program_on = self.builder_on.get()    
        self.program_off = self.builder_off.get()   

    def set_proximity(self, value):
        on = 1                    
        steps = len(self.program_on) - 1                  
        step = min(steps, max(0, int(round(steps * on)))) 

        if value == 0:
            sleep_time = 0.100
        elif value == 1:
            sleep_time = 0.500
        elif value == 2:
            sleep_time = 1
        
        while True:
            intensity_on = 0
            sleep(0.500)
            for level in LEVELS:
                intensity_on = intensity_on + 0.20
                if self.current_space == 0:
                    self.set_all(intensity_on) 
                    self.set_all_off()
                elif self.current_space == 1:
                    self.set_all(intensity_on) 
                    sleep(0.10)
                elif self.current_space == 2:
                    self.set_all(intensity_on) 
                    sleep(0.50)
                else:
                    self.set_all_off()

class MindwaveLights(Lights):
    program_on = None
    program_off = None
    
    def __init__(self, *args, **kwargs):
        Lights.__init__(self, *args, **kwargs)
        self.generate_program()
    
    def generate_program(self):
        builder_on = ProgramBuilder()
        builder_off = ProgramBuilder()
        
        for level in LEVELS:
            for c in level:
                builder_on.add(c, 1)
                builder_off.add(c, 0)
                
            builder_on.step()
            builder_off.step()

        self.program_on = builder_on.get()
        self.program_off = builder_off.get()

    def intensity_map(self, value):
        return max(0.0, float(value - 50) / (90.0 - 50.0))
    
    def set_mindwave(self, value):
        on = self.intensity_map(value)
        steps = len(self.program_on) - 1
        step = min(steps, max(0, int(round(steps * on))))
        
        if self.debug:
            print "LIGHTS:", str(round(on * 100)) + "%", program[step:step+1]
            
        self.run_program(self.program_on[:step+1] + self.program_off[step+1:])

class HeartrateLights(Lights):
    program = None
    bpm = 1
    _running = False
    
    def __init__(self, *args, **kwargs):
        Lights.__init__(self, *args, **kwargs)
        self.program = None
        self.bpm = 1
        self._running = False
        self.generate_program()
    
    def generate_program(self):
        builder = ProgramBuilder()
        step_duration = lambda: (60.0 / float(self.bpm)) / float(len(self.program))
        
        self.program = builder.add(None, 1).lerp(1, 10).get()
        program_rev = list(self.program)
        program_rev.reverse()
        self.program += program_rev
        
        # HACK: lerp should allow a callable or not depend on duration if desired
        for i, entry in enumerate(self.program):
            self.program[i] = (step_duration, entry[1])
    
    def generate_program_old(self):
        builder = ProgramBuilder()
        step_duration = lambda: (60.0 / float(self.bpm)) / float(len(self.program))
        
        for level in LEVELS:
            for channel in level:
                builder.add(channel, 1)
            for level2 in LEVELS:
                if level2 != level:
                    for channel in level2:
                        builder.add(channel, 0)
            
            builder.step(step_duration)
        
        self.program = builder.get()
    
    def start(self):
        if not self._running:
            self._running = True
            task = threading.Thread(target=self._run)
            task.setDaemon(True)
            task.start()
    
    def stop(self):
        self._running = False
    
    def _run(self):
        while self._running:
            self.run_program(self.program)
    
    def set_bpm(self, bpm):
        if bpm <= 0:
            raise ValueError, "Invalid BPM"
        
        self.bpm = bpm
        self.start()
