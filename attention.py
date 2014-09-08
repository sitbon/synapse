import sys
import serial
from cStringIO import StringIO
import struct
from collections import namedtuple

import logging
import logging.handlers

import thinkgear 
import requests

_log = logging.getLogger(__name__)

_bytelog = logging.getLogger(__name__+'.bytes')
_bytelog.propagate = False


def main():
    print __name__

    global packet_log
    packet_log = []
    logging.basicConfig(level=logging.DEBUG)

    is_recording = False
    
    for pkt in thinkgear.ThinkGearProtocol('/dev/rfcomm0').get_packets():    
	for d in pkt:
          if isinstance(d, thinkgear.ThinkGearAttentionData):
		print d.value
          
	  if isinstance(d, thinkgear.ThinkGearAttentionData) and d.value >= 60:
	        print is_recording	
		if d.value >= 80:
		    if is_recording == False:
			print 'starting recording'
		    	#r = requests.get('http://192.168.42.1/setting/cgi-bin/fd_control_client?func=fd_taking_photo')
		    	#r = requests.get('http://192.168.42.1/setting/cgi-bin/fd_control_client?func=fd_set_capture_mode&data=0')
		    	#r = requests.get('http://192.168.42.1/setting/cgi-bin/fd_control_client?func=fd_record')
			is_recording = True
		elif d.value < 80 and d.value >= 50:
		    #stop recording
		    if is_recording == True:
		        print 'stopping recording'
	            	#r = requests.get('http://192.168.42.1/setting/cgi-bin/fd_control_client?func=fd_record')
			is_recording = False
		    print "Attention is elevated..."   
		    print d.value	
		break
	  elif isinstance(d, thinkgear.ThinkGearAttentionData) and d.value < 50:
		print is_recording
	        print "Are you distracted?"
		d.value
		if is_recording == True:
		    print 'stopping recording'
                    #r = requests.get('http://192.168.42.1/setting/cgi-bin/fd_control_client?func=fd_record')
		    is_recording = False     

	sys.stdout.flush()

if __name__ == '__main__':
    main()
