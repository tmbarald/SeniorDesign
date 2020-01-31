import time
import RPi.GPIO as GPIO

def t26():
    GPIO.output(26, True)
    time.sleep(1)
    GPIO.output(26, False)

def main1():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)
    i = 1
    while i:
       if i % 2 == 0:
           t26()
       else:
           time.sleep(1)
       if i == 100:
           print("Done")
           break
       i += 1
    GPIO.cleanup()
       
       

main1()     



'''
#input 
GPIO.setup(17, GPIO.IN, pull_up_down = GPIO.PUD_UP)
GPIO.input(17)
GPIO.input(17)
'''