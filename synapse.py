import sys
import time
import requests
import threading

import attention
import heartrate
import proximity
import lights

DATA_URL = "http://192.168.42.1/data/"
ENABLE_PUBLISH = True 

class Synapse:
    def __init__(self):
        self.attention =  attention.Attention()
        self.heartrate = heartrate.HeartBeat()
        self.proximity = None #proximity.Proxemic()
        self.lights = lights.Lights()
        self.lights_heartrate = lights.HeartrateLights()

    def start(self):
        self.lights.reset()
        #self.lights_heartrate.set_bpm(60)
        self.heartrate.monitor_heartrate(self.update_heartrate)
        self.attention.monitor_attention(self.update_attention)
        #self.proximity.monitor_space(lambda x: True, self.update_proximity)
        #self.lights_heartrate.set_bpm(int(self.heartrate.current_value))

    def update_heartrate(self, value):
        print >>sys.stderr, "EKG:", value
        self.publish_value(self.heartrate, value)
        return True

    def update_attention(self, value):
        print >>sys.stderr, "EEG:", value
        self.publish_value(self.attention, value)
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

        task = threading.Thread(target=do_post)
        task.setDaemon(True)
        task.start()
        

def main(args):
    synapse = Synapse()
    synapse.start()
    
    while True:
        pass

if __name__ == '__main__':
    main(sys.argv[1:])
