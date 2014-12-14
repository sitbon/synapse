import sys
import subprocess
import thinkgear 
import requests
import camera 
from threading import Thread

value = 0
def main():
    sp_lights = subprocess.Popen(['python', 'led.py', 'mindwave'],
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE, shell = False)
    global value
    Thread(target=handleCamera).start()
    for pkt in thinkgear.ThinkGearProtocol('/dev/rfcomm0').get_packets():
      for d in pkt:
          if isinstance(d, thinkgear.ThinkGearAttentionData):
                print d.value
		value = d.value
                print 'activating lights'
                sp_lights.stdin.write(str(d.value) + '\n')
                sys.stdout.flush()

def handleCamera():
  is_recording = False
  while True:
    if value >= 40:
      if not is_recording:
        camera.take_picture()
        camera.start_recording()
        is_recording = True
    else:
      if is_recording:
        camera.stop_recording()
        is_recording = False

def handleCameraData():
  print 'copying latest picture & video to web server'

                
if __name__ == '__main__':
    main()
