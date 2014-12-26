import sys
import time
import requests
from multiprocessing import Process, Value 
from threading import Thread
import subprocess

import attention
import heartrate
import proximity
import lights
import button 
import camera

DATA_URL = "http://192.168.42.1/data/"
ENABLE_PUBLISH = True 

class Synapse:
    HEARTRATE = 0    
    ATTENTION = 1 

    def __init__(self):
        self.attention = attention.Attention()
        self.heartrate = heartrate.HeartBeat()
        self.proximity = proximity.Proxemic()
        self.button = button.Button()
        
        self.lights = lights.Lights()
        self.lights_heartrate = lights.HeartrateLights()
        self.lights_mindwave = lights.MindwaveLights()
        self.lights_proximity = lights.ProximityLights()
        
        self.animation = Value('d',self.ATTENTION, lock=True) 
        self.previous_animation = Value('d',self.ATTENTION, lock=True)

        self.attention_value = Value('d', 0, lock=True)
        self.heartrate_value = Value('d', 0, lock=True)
        self.lights_process = Process(target=self._animate_lights)
       
        self.copying_files = Value('b', False, lock=True) 
        self.camera_process = Process(target=self.handle_camera)

    def _switch_animation_listener(self):
        print 'toggled!'
        if self.animation.value == self.ATTENTION:
            print 'attention is true'
            self.previous_animation.value = self.ATTENTION
            self.animation.value = self.HEARTRATE 
        else:
            print 'heartrate is true'
            self.previous_animation.value = self.HEARTRATE
            self.animation.value = self.ATTENTION 
        return True

    # note sure the best way to do this
    # maybe a callback but if they press the button and the sensor
    # is toggled we don't want to wait too long to repaint animation 
    # because they may think the button didn't work and will push it again
    def _animate_lights(self): 
        while True:
            time.sleep(1)
            try:
                if self.animation.value == self.ATTENTION:
                    if self.previous_animation.value == self.HEARTRATE:
                        self.lights_heartrate.stop()
                    print 'attention lights' 
                    self.lights_mindwave.set_mindwave(self.attention_value.value)
                else:
                    print 'heartbeat lights'
                    self.lights_heartrate.set_bpm(self.heartrate_value.value)
            except: 
                pass

    def start(self):
        self.button.monitor_button(self._switch_animation_listener)
        self.lights.reset()
        self.heartrate.monitor_heartrate(self.update_heartrate)
        self.attention.monitor_attention(self.update_attention)
        self.proximity.monitor_space(lambda x: True, self.update_proximity)
        self.lights_process.start()
        self.camera_process.start()
 
    def update_heartrate(self, value):
        print >>sys.stderr, "EKG:", value
        self.publish_value(self.heartrate, value)        
        self.heartrate_value.value = value
        return True

    def update_attention(self, value):
        print >>sys.stderr, "Attention:", value
        self.publish_value(self.attention, value)
        self.attention_value.value = value
        return True
       
    def update_proximity(self, value):
        print >>sys.stderr, "PRX:", value
        self.publish_value(self.proximity, value)
        return True
        
    def publish_value(self, source, value):
        if not ENABLE_PUBLISH:
            return
        #timestamp = time.now()
        if source is self.attention:
            url_id = "attention"
        elif source is self.heartrate:
            url_id = "heartrate"
        elif source is self.proximity:
            url_id = "proximity"
        else:
            raise ValueError, "invalid data source"

        do_post = lambda: requests.post(DATA_URL + url_id, {"value" : str(value)})

        task = Process(target=do_post)
        #task.setDaemon(True)
        task.start()
        
    def handle_camera(self):
        recording = False 
        while True:
            if self.attention_value.value >= 80:
                if not recording:
                    camera.take_picture()
                if self.attention_value.value >= 80:
                    camera.start_recording()
                    recording = True
            else:
                if recording:
                    camera.stop_recording()
                    recording = False

                    if not self.copying_files.value:
                        Process(target=self.copy_camera_files).start()

    def copy_camera_files(self):
       self.copying_files.value = True
       files = camera.get_latest_files(None)
       if len(files) > 0:
          for file in files:
              print 'copying latest pictures & videos to web server'
              sp = subprocess.call(['wget', '-nc', file, '-P', 'web_server/downlods/'])
              
       self.copying_files.value = False 

def main(args):
    synapse = Synapse()
    synapse.start()
    
    while True:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])
