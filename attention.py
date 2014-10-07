import sys
import subprocess
import thinkgear 
import requests

def main():
    for pkt in thinkgear.ThinkGearProtocol('/dev/rfcomm0').get_packets():
        for d in pkt:
            if isinstance(d, thinkgear.ThinkGearAttentionData):
                print d.value
                sys.stdout.flush()

if __name__ == '__main__':
    main()
