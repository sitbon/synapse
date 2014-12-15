import requests
import re

IP = '192.168.42.20'
LIST_ALL_FILES = 'fd_list_files&0'
LIST_NEW_FILES = 'fd_list_files&referenceFile='
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

def get_latest_files(reference_file):
    print 'getting file names'
    camera_files = []
    
    # this command has two forms
    # you can either ask camera to return all files or just 
    # files created after a specific file that you know exists on the camera
    # so this if statements is figuring out which version you'd like to use
    if reference_file is None:
      entries = run(LIST_ALL_FILES)
    else:
      # filepath is relative to DCIM folder so that's what the camera wants
      # but we return the whole path, so I'm stripping out everything before and including DCIM
      reference_file = str.split(reference_file, 'DCIM/')[1]
      entries = run(LIST_NEW_FILES + reference_file)
    
    # we an get a TypeError if there are no new files created
    # or no files at all on camera. Is it a problem that I just pass?
    try:
        #camera returns all files wrapped in json objects, but the outside is some xml syntax
        #so I couldn't just do json.load() so I decided to use some regex to just strip out 
        # the relative filepath, leaving behind createtime and size
        files = re.findall("(100DRIFT\S\w+\W\w+)", entries)
        for file in files:
            file = 'http://{0}/DCIM/{1}'.format(IP, file) 
            camera_files.append(file)
    except TypeError:
       pass
  

    return camera_files 
    
def run(request):
    # decided to have just one function that executes the requests call
    # we catch the one type of error I've seen the camera do
    # maybe this is a good place to then try to bring hostapd back up or reboot camera
    # but will need work on hardware side some soldering of battery stuff and I'm not sure
    try:
        base_url = 'http://{0}/setting/cgi-bin/fd_control_client?func='.format(IP)
        r = requests.get(base_url + request)
        return r.text
    except requests.exceptions.ConnectionError, e:
        print 'restoring wifi connection with camera'
        print e
