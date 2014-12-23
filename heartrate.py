import subprocess
from time import sleep
from threading import Thread
from nbstreamreader import NonBlockingStreamReader

class HeartBeat():
    current_value = None
    is_alive = False
    gatttool_thread = None
    gatttool_subprocess = None      
    nbsr_heartrate = None

    def __init__(self):
        self.gatttool_thread = None

    def monitor_heartrate(self, callback):
        Thread(target=self._start_reading, args=(callback,)).start()

    def _start_reading(self, callback):
        self.gatttool_subprocess = subprocess.Popen(['./gatttool', '-t', 'random', '-b', 'DD:FB:8B:5B:7F:28', '-I'],
                                               stdin = subprocess.PIPE, 
                                               stdout = subprocess.PIPE, 
                                               stderr = subprocess.PIPE, shell = False)
       
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
             print line
             if line is not None:
                 if line.find('Connection successful') > 0:
                     break
             else:
                 sleep(0.500)
      
        # this command tells gatttool to print heart rate information
        self.gatttool_subprocess.stdin.write('\nchar-write-req 1b 0100\n')
        
        while True:
            try:
                line = self.nbsr_heartrate.readline(1)
                if line is not None:
                    if line.find('Notification handle') > 0:
                        right_side = line.split('value:')
                        numbers = right_side[1].split(' ')
                        current_value = int('0x' + numbers[2], 16)
                        #print current_value
                        if not callback(current_value):
                            return
                        sleep(1)
            except TypeError:
                pass

if __name__ == '__main__':
    wahoo = HeartBeat()
          
