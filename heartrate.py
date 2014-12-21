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
        self.gatttool_thread = Thread(target=self.start_reading).start()

    def start_reading(self):
        self.gatttool_subprocess = subprocess.Popen(['./gatttool', '-t', 'random', '-b', 'DD:FB:8B:5B:7F:28', '-I'],
                                               stdin = subprocess.PIPE, 
                                               stdout = subprocess.PIPE, 
                                               stderr = subprocess.PIPE, shell = False)
       
        sleep(2) 
        self.nbsr_heartrate = NonBlockingStreamReader(self.gatttool_subprocess.stdout)        
        self.gatttool_subprocess.stdin.write('\n')
        self.gatttool_subprocess.stdin.write('connect')
        self.gatttool_subprocess.stdin.write('\n')
        sleep(2) 
        for x in range(0, 10):
             print 'before printing line' 
             line = self.nbsr_heartrate.readline(0.1)
             print line
             print 'after printing line'
             if line is not None:
                 if line.find('Connection successful') > 0:
                     print "should be successful: " + line
                     break
             else:
                 sleep(5)
      
        sleep(5)
        self.gatttool_subprocess.stdin.write('\n') 
        self.gatttool_subprocess.stdin.write('char-write-req 1b 0100')
        self.gatttool_subprocess.stdin.write('\n')
        sleep(10) 
        while True:
            try:
                line = self.nbsr_heartrate.readline(1)
                print line
                if line is not None:
                    if line.find('Notification handle') > 0:
                        right_side = line.split('value:')
                        numbers = right_side[1].split(' ')
                        current_value = int('0x' + numbers[2], 16)
                        print current_value
                        sleep(1)
            except TypeError:
                pass

if __name__ == '__main__':
    wahoo = HeartBeat()
          
