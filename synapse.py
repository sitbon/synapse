import sys
import time
import requests
from multiprocessing import Process, Value 
import subprocess
import signal

import attention
import heartrate
import proximity
import lights
import button 
import camera

DATA_URL = "http://192.168.42.1/data/"
ENABLE_PUBLISH = False

class Synapse:
    STATE_HEART_MIND = 0
    STATE_PROXIMITY = 1
    STATES = [STATE_HEART_MIND, STATE_PROXIMITY]

    def __init__(self):
        self.attention = attention.Attention()
        self.heartrate = heartrate.HeartBeat()
        self.proximity = proximity.Proxemic()
        self.button = button.Button()

        self.state_value = Value('i', Synapse.STATES[0])
        self.attention_value = Value('d', 0)
        self.heartrate_value = Value('i', 60)
        self.proximity_space_value = Value('i', -1)
        self.proximity_value = Value('d', 0)

        self.lights = lights.SynapseLights()
        self.lights.set_heart(self.heartrate_value)
        self.lights.set_mind(self.attention_value)
        self.lights.set_space(self.proximity_space_value)
        self.lights.set_space_enable(self.state_value)

        self.copying_files = Value('b', False)
        self.camera_process = Process(target=self.handle_camera)

    def start(self):
        self.button.monitor_button(self.on_button)
        self.proximity.monitor_space(self.update_proximity_space, self.update_proximity)

        self.heartrate.monitor_heartrate(self.update_heartrate)
        self.attention.monitor_attention(self.update_attention)
        self.camera_process.start()

        self.lights.reset()
        self.lights.start()

    def stop(self):
        self.lights.stop()

    def join(self):
        try:
            while True:
                if self.lights.join(0.500):
                    break
        except KeyboardInterrupt:
            self.on_interrupt()

    def on_interrupt(self):
        print >>sys.stderr, "\nInterrupt caught"
        self.stop()
        sys.exit(0)

    def on_button(self):
        self.state_value.value = Synapse.STATES[(self.state_value.value + 1) % len(Synapse.STATES)]
        print >>sys.stderr, "BUTTON: state=" + str(self.state_value.value)
        return True

    def update_heartrate(self, value):
        if self.state_value.value == Synapse.STATE_HEART_MIND:
            print >>sys.stderr, "EKG:", value
        self.heartrate_value.value = value
        self.publish_value(self.heartrate, value)
        return True

    def update_attention(self, value):
        if self.state_value.value == Synapse.STATE_HEART_MIND:
            print >>sys.stderr, "Attention:", value
        self.attention_value.value = value
        self.publish_value(self.attention, value)
        return True

    def update_proximity_space(self, value):
        if self.state_value.value == Synapse.STATE_PROXIMITY:
            print >>sys.stderr, "SPACE:", value
        self.proximity_space_value.value = value
        return True

    def update_proximity(self, value):
        if self.state_value.value == Synapse.STATE_PROXIMITY:
            print >>sys.stderr, "PRX:", value
        self.proximity_value.value = value
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
        elif source is camera:
            if '.JPG' in value:
                url_id = 'image'
            elif '.mp4' in value:
                url_id = 'video'
            else:
                raise ValueError, "invalid data source"
            print url_id
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
                    print 'sleeping 2 seconds'
                    time.sleep(2)
                    if self.attention_value.value >= 80:
                        camera.start_recording()
                        recording = True
                        print 'sleeping 2 seconds'
                        time.sleep(2)
            else:
                if recording:
                    camera.stop_recording()
                    recording = False
                          
                    if not self.copying_files.value:
                        Process(target=self.copy_camera_files).start()
                        print 'sleeping 1 second'
                        time.sleep(1)

    def copy_camera_files(self):
       self.copying_files.value = True
       files = camera.get_latest_files(None)
       if len(files) > 0:
          for file in files:
              print 'copying latest pictures & videos to web server'
              child = subprocess.Popen(['wget', '-nc', file, '-P', '/home/root/synapse/web_server/images/'],
                                                                   stdout=subprocess.PIPE,
                                                                   stderr=subprocess.PIPE)
              streamdata = child.communicate()
              stdout = streamdata[0]
              stderr = streamdata[1]
              print streamdata
              if 'already there' not in stderr:
                  print 'publishing!'
                  value = file.replace('http://' + camera.IP + '/DCIM/100DRIFT/', '')
                  self.publish_value(camera, value)        
 
       self.copying_files.value = False 

def main(args):
    synapse = Synapse()
    synapse.start()
    synapse.join()

if __name__ == '__main__':
    main(sys.argv[1:])
