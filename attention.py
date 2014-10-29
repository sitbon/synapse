import sys
import subprocess
import thinkgear 
import requests

def main():
    sp_lights = subprocess.Popen(['python', 'led.py', 'mindwave'],
                                stdin = subprocess.PIPE,
                                stdout = subprocess.PIPE,
                                stderr = subprocess.PIPE, shell = False)

    for pkt in thinkgear.ThinkGearProtocol('/dev/rfcomm0').get_packets():
        for d in pkt:
            if isinstance(d, thinkgear.ThinkGearAttentionData):
                print d.value
                sp_lights.stdin.write(str(d.value) + '\n')
                sys.stdout.flush()
                
if __name__ == '__main__':
    main()
