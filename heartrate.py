import sys
import subprocess
from time import sleep
from multiprocessing import Process
from nbstreamreader import NonBlockingStreamReader
import atexit

MAC_ADDRESS = 'DD:FB:8B:5B:7F:28'
#MAC_ADDRESS = 'D4:48:C2:4C:A0:19'

class HeartBeat():
    current_value = None
    is_alive = False
    gatttool_thread = None
    gatttool_subprocess = None      
    nbsr_heartrate = None

    def __init__(self):
        self.gatttool_thread = None

    def monitor_heartrate(self, callback):
        Process(target=self._start_reading, args=(callback,)).start()

    def _start_reading(self, callback):
        self.gatttool_subprocess = subprocess.Popen(['/home/root/synapse/gatttool', '-t', 'random', '-b', MAC_ADDRESS, '-I'],
                                               stdin = subprocess.PIPE, 
                                               stdout = subprocess.PIPE, 
                                               stderr = subprocess.PIPE, shell = False)

        def cleanup():
            if self.gatttool_subprocess is not None:
                try:
                    self.gatttool_subprocess.kill()
                except:
                    pass

        atexit.register(cleanup)

        # wait for process to come up
        for x in range (0, 10):
            if self.gatttool_subprocess.poll() is None:
                sleep(0.500)

        # this stream reader does not block if gatttool fails send anything to stdout
        self.nbsr_heartrate = NonBlockingStreamReader(self.gatttool_subprocess.stdout)
        
        # connect bt le wahoo heartrate monitor and wait for connect commadn to be processed
        self.gatttool_subprocess.stdin.write('\nconnect\n')
        
        for x in range(0, 10):
             line = self.nbsr_heartrate.readline(0.1)
             if line is not None:
                 if line.find('Connection successful') > 0:
                     break
             else:
                 sleep(0.500)
      
        # this command tells gatttool to print heart rate information
        #self.gatttool_subprocess.stdin.write('\nchar-write-req 1b 0100\n')
        self.gatttool_subprocess.stdin.write('\nchar-write-req 18 0100\n')

        while True:
            sleep(1)
            try:
                line = self.nbsr_heartrate.readline(1)
                if line is not None:
                    if line.find('Notification handle') > 0:
                        right_side = line.split('value:')
                        numbers = right_side[1].split(' ')
                        current_value = int('0x' + numbers[2], 16)
                        if not callback(current_value):
                            return
            except TypeError:
                pass

def update_heartrate(value):                                      
    print >>sys.stderr, "EKG:", value                                   
    return True   

if __name__ == '__main__':
    wahoo = HeartBeat()
    wahoo.monitor_heartrate(update_heartrate)
    sleep(5)

    while True:
        if wahoo.current_value is not None:
            print wahoo.current_value      
