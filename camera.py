import requests

IP = '192.168.42.20'
#CAMERA_API_URL = 'http://192.168.42.20/setting/cgi-bin/fd_control_client?func={0}'
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

def run(request):
  try:
    base_url = 'http://{0}/setting/cgi-bin/fd_control_client?func='.format(IP)
    r = requests.get(base_url + request)
    print r
  except requests.exceptions.ConnectionError, e:
    print 'restoring wifi connection with camera'
    print e
