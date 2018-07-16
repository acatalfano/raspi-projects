#!/usr/bin/env python3

# Displays clock
# Wire as such:
# GPIO Pin -- Module Pin
# 21 -R- 1       22 -R- 7
# 20 -R- 2        5 --- 8
# 16 -R- 3        6 --- 9
# 12 -R- 4       13 -R- 10
# 25 -R- 5       19 -R- 11
# 18 --- 6       26 --- 12
# * R indicates a resistor in the connection

import RPi.GPIO as GPIO
import time

def main():
    
    GPIO.setmode(GPIO.BCM)
    
    segments = [21,20,12,25,22,13,19]
    decimal  = 16
    digits   = [26,6,5,18]
    
    GPIO.setup(segments, GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(decimal,  GPIO.OUT, initial=GPIO.LOW)
    GPIO.setup(digits,   GPIO.OUT, initial=GPIO.HIGH)
    
    numbers = { ' ': [0,0,0,0,0,0,0],
                '0': [1,1,1,0,1,1,1],
                '1': [0,0,1,0,1,0,0],
                '2': [1,1,0,1,1,0,1],
                '3': [0,1,1,1,1,0,1],
                '4': [0,0,1,1,1,1,0],
                '5': [0,1,1,1,0,1,1],
                '6': [1,1,1,1,0,1,1],
                '7': [0,0,1,0,1,0,1],
                '8': [1,1,1,1,1,1,1],
                '9': [0,0,1,1,1,1,1]
              }
    
    try:
        while True:
            locTime = time.localtime()
            minutes = locTime.tm_min
            hours   = locTime.tm_hour
            
            pm = bool( int(hours / 12) )
            hours = hours % 12
            
            mins_ones = str(minutes % 10)
            mins_tens = str(int( minutes / 10 ))
            hrs_ones  = str(hours % 10)
            hrs_tens  = str(int( hours / 10 ))
            
            # first display the hours through digits[0:1]
            # with digits[1] given a decimal point to represent the colon on a digital clock
            GPIO.output(segments,   numbers[hrs_tens])
            GPIO.output(digits[0],  GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(digits[0],  GPIO.HIGH)

            GPIO.output(segments,   numbers[hrs_ones])
            GPIO.output(decimal,    GPIO.HIGH)
            GPIO.output(digits[1],  GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(digits[1],  GPIO.HIGH)
            GPIO.output(decimal,    GPIO.LOW)
            
            # finally display minutes through digits[2:3]
            GPIO.output(segments,   numbers[mins_tens])
            GPIO.output(digits[2],  GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(digits[2],  GPIO.HIGH)

            GPIO.output(segments,   numbers[mins_ones])
            if pm:
                GPIO.output(decimal,    GPIO.HIGH)
            GPIO.output(digits[3],  GPIO.LOW)
            time.sleep(0.001)
            GPIO.output(digits[3],  GPIO.HIGH)
            if pm:
                GPIO.output(decimal,    GPIO.LOW)
            
    finally:
        GPIO.cleanup()

    

if __name__ == '__main__':
    main()
