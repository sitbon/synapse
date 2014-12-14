import requests
import re

IP = '192.168.42.20'
#CAMERA_API_URL = 'http://192.168.42.20/setting/cgi-bin/fd_control_client?func={0}'
GET_VIDEO_FILE = 'fd_get_latest_media_file_2&type=0'
GET_PHOTO_FILE = 'fd_get_latest_media_file&type=1'
LIST_FILES = 'fd_list_files&0'
PHOTO_MODE = 'fd_set_capture_mode&data=1' 
VIDEO_MODE = 'fd_set_capture_mode&data=0'
RECORD = 'fd_record'

def take_picture():
  print 'taking picture'
  run(PHOTO_MODE)
  run(RECORD)

def start_recording():
  print 'start recording'
  run(VIDEO_MODE)
  run(RECORD)

def stop_recording():
  print 'end recording'
  run(RECORD)

def get_latest_files():
  print 'getting file names'
  entries = run(LIST_FILES)
  files = re.findall("(100DRIFT\S\w+\W\w+)", entries)
  for file in files:
    print file
    
def run(request):
  try:
    base_url = 'http://{0}/setting/cgi-bin/fd_control_client?func='.format(IP)
    r = requests.get(base_url + request)
    print r.text
    return r.text
  except requests.exceptions.ConnectionError, e:
    print 'restoring wifi connection with camera'
    print e
