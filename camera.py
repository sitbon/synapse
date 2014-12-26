import requests
import re
from time import sleep

IP = '192.168.42.21'
GET_VIDEO_FILE = 'fd_get_latest_media_file_2&type=0'
GET_PHOTO_FILE = 'fd_get_latest_media_file&type=1'
LIST_ALL_FILES = 'fd_list_files&0'
LIST_NEW_FILES = 'fd_list_files&referenceFile='
PHOTO_MODE = 'fd_set_capture_mode&data=1' 
VIDEO_MODE = 'fd_set_capture_mode&data=0'
RECORD = 'fd_record'

def take_picture():
  print 'taking picture'
  run(PHOTO_MODE)
  run(RECORD)
  sleep(2)

def start_recording():
  print 'start recording'
  run(VIDEO_MODE)
  run(RECORD)
  sleep(2)

def stop_recording():
  print 'end recording'
  run(RECORD)
  sleep(2)

def get_latest_files(reference_file):
  print 'getting file names'
  camera_files = []
  if reference_file is None:
    entries = run(LIST_ALL_FILES)
  else:
    reference_file = str.split(reference_file, 'DCIM/')[1]
    entries = run(LIST_NEW_FILES + reference_file)

  try:
    files = re.findall("(100DRIFT\S\w+\W\w+)", entries)
    for file in files:
      file = 'http://{0}/DCIM/{1}'.format(IP, file) 
      camera_files.append(file)
  except TypeError:
     pass
 
  return camera_files 
    
def run(request):
  try:
    base_url = 'http://{0}/setting/cgi-bin/fd_control_client?func='.format(IP)
    r = requests.get(base_url + request)
    return r.text
  except requests.exceptions.ConnectionError, e:
    print 'restoring wifi connection with camera'
    print e
