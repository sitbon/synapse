import sys
import thinkgear 
import camera 
from multiprocessing import Process
from time import sleep

class Attention():
    def monitor_attention(self, callback):
        Process(target=self._start_reading, args=(callback,)).start()

    def _start_reading(self, callback):
        while True:
            try:                                  
                for pkt in thinkgear.ThinkGearProtocol('/dev/rfcomm0').get_packets():
                    for d in pkt:                                                                                        
                        if isinstance(d, thinkgear.ThinkGearAttentionData):
                            current_value = int(d.value)
                            if not callback(current_value):
                                return
            except:
                pass
 

def update_attention(value):                                      
    print >>sys.stderr, "EEG:", value                             
    return True  

  
if __name__ == '__main__':
    #main()
    a = Attention()
    a.monitor_attention(update_attention)
    sleep(5)

    while True:
        sleep(1)
        print a.current_value
