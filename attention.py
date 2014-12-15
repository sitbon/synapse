import sys
import subprocess
import thinkgear 
import requests
import camera 
from threading import Thread
from time import sleep

# these are here because I'm not using a queue for the threads
# should I use a queue? 
value = 0
last_file_copied = None
copying_files = False

""" 
    Assumes init_bluetooth.sh already set up the bluetooth connection
    then reads attention value and activates the lights based on it.
"""
def main():
    # this is here because I was trying to be consistent with dress.py
    # but maybe it would be better to change it to led.mindwave(d.value)
    # initially dress.py was driving everything and attention.py was just providing 
    # d.value to std.out 
    sp_lights = subprocess.Popen(['python', 'led.py', 'mindwave'],
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE, shell = False)
    
    # have to mark it global again because we're not using a queue 
    # I'm interested to know if this is just a terrible idea and what consequences 
    # we could have?
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

"""
   We want to take a picture when the attention value is above 80 and then record a video for the duration 
   that it stays above 80. The camera will lock up if it gets too many http get requests too fast and so I added
   a 1 second sleep you'll see below. The camera also takes 1 to 2 seconds to process a "start/stop" recording call
   so we will sometimes record when eeg value has dropped below 80. 
"""  
def handleCamera():
  is_recording = False
  while True:
    # added this sleep here to give the main() thread a chance to read values from bluetooth
    # i'm assumign this is the effect of cpython global interpreter lock? 
    # again would using a queue and/or threading.Event object be better? 
    # what's the advantage? does this implementation make your hair stand up?  
    sleep(1)
    if value >= 40:
      if not is_recording:
        camera.take_picture()
        camera.start_recording()
        is_recording = True
    else:
      if is_recording:
        camera.stop_recording()
        is_recording = False
      
        # i was really lazy at this point and this is how i decided 
        # to copy files. please make a better suggestion if this bothers you
        if not copying_files:
          Thread(target=handleCameraData).start()

""" Copies files from camera to web_Server/downloads/ for now, please make a suggestion for a better location?
    using wget with -nc option to only copy files that aren't already in downloads folder
"""
def handleCameraData():
  global last_file_copied
  global copying_files
  copying_files = True

  # i'm using wget to copy files i know i could have used libcurl
  # but i didn't know wat the advantage would be or the risk in doing it this way
  # also because i'm using the -nc flag we probably don't need to track last_file_copied
  # a new wget process gets issued for every file that is being copied and they could all be running at the same time
  # this could be a total disaster, but I didn't see one while testing so I left it
  # i'm open to suggestions 
  print 'copying latest picture & video to web server'
  files = camera.get_latest_files(last_file_copied)  
  if len(files) > 0:
    for file in files:
       subprocess.Popen(['wget', '-nc', file,'-P', 'web_server/downloads/'])
    last_file_copied = files[-1]
 
  copying_files = False 
  
if __name__ == '__main__':
    main()
