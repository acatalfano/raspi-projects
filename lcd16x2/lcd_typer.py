#!/usr/bin/env python3

# lcd_typer.py
#
# Program to drive a 16x2 LCD screen to behave as a small
# typing interface
#
# All keys that register as 1-length character input
# are parsed as content (except for the TAB key, but including the SPACE bar)
#
# Functional keys that are handled are:
# Backspace, Delete, Home, End, all 4 arrow keys
#
# To terminate the loop, press either: Ctrl-C or Ctrl-D
#
#
#
# Wire the 16 pins as follows:
# 1  --> Ground
# 2  --> VDD (+5.0V)
# 3  --> Ground
#           OR --> Potentiometer --> Ground (to have control of the contrast)
# 4  --> GPIO18
# 5  --> Ground
# 6  --> GPIO23
# 7  --> [Vacant]
# 8  --> [Vacant]
# 9  --> [Vacant]
# 10 --> [Vacant]
# 11 --> GPIO12
# 12 --> GPIO16
# 13 --> GPIO20
# 14 --> GPIO21
# 15 --> 1K Resistor --> VDD (+5.0V)
#           OR --> Potentiometer --> VDD (+5.0V) (to have control of the backlight brightness)
# 16 --> Ground

import sys
sys.path.append('.')

import RPi.GPIO as GPIO
import time
import getKey

LCD_RS = 18
LCD_E  = 23
LCD_D4 = 12
LCD_D5 = 16
LCD_D6 = 20
LCD_D7 = 21

LCD_DATA = [ LCD_D7, LCD_D6, LCD_D5, LCD_D4 ]


WIDTH       = 16
LCD_CHAR    = GPIO.HIGH
LCD_CMD     = GPIO.LOW

E_DOWN      = 0.0005
E_UP        = 0.0005

LINE1_START = 0x80
LINE2_START = 0xC0

LINE1_END   = 0x8F
LINE2_END   = 0xCF

def init():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(LCD_E,       GPIO.OUT)
    GPIO.setup(LCD_RS,      GPIO.OUT)
    GPIO.setup(LCD_DATA,    GPIO.OUT)
    
    lcd_out(LCD_CMD, 0x33) # init command
    lcd_out(LCD_CMD, 0x32) # init command
    lcd_out(LCD_CMD, 0x28) # 4-bit mode, 2 lines, 5x8 dot matrix
    lcd_out(LCD_CMD, 0x08) # display off, cursor off, blink off
    lcd_out(LCD_CMD, 0x01) # clear display
    lcd_out(LCD_CMD, 0x06) # cursor increment (L-to-R oriented) and no shifting display
    lcd_out(LCD_CMD, 0x0D) # display on, cursor off, blink on
    
    time.sleep(E_DOWN)



def lcd_out(mode, data):
    # output data as per mode (one of LCD_CHAR or LCD_CMD)

    GPIO.output(LCD_RS, mode) # Register Select Bit (command vs literal)
    
    data_bits = bitlist(data)
    GPIO.output(LCD_DATA, data_bits[:4])
    pulse_output()
    GPIO.output(LCD_DATA, data_bits[4:])
    pulse_output()


def pulse_output():
    # switch enable pin to on, wait, then switch it off
    
    time.sleep(E_DOWN)
    GPIO.output(LCD_E, GPIO.HIGH)
    time.sleep(E_UP)
    GPIO.output(LCD_E, GPIO.LOW)
    time.sleep(E_DOWN)
    






def bitlist(n):
    # convert a number into a list of binary digits with MSB at index == 0
    nList = [digit=='1' for digit in bin(n)[2:]]

    if nList:
        while len(nList) != 8:
            nList.insert(0,False)

    else:
        nList = [False for i in range(8)]
    
    return nList






def writeChar(c, firstLine, count):
    # handle ctrl-C and ctrl-D to end the loop
    if c in ['keyboard-interrupt', 'end-of-file']:
        raise KeyboardInterrupt
    
    
    # up arrow key moves cursor up from line 2 to line 1
    elif c == 'u-arr':
        if not firstLine:
            addr = LINE1_START + count
            firstLine = True
            lcd_out(LCD_CMD, addr)
        
        
    # right arrow key moves cursor right as long as the position
    # is not the end of the second line
    elif c == 'r-arr':
        if count != 15:
            count += 1
            addr = LINE2_START - (0x40 * firstLine) + count
            lcd_out(LCD_CMD, addr)
        
        elif firstLine:
            count = 0
            firstLine = False
            lcd_out(LCD_CMD, LINE2_START)
        
        
        
    # left arrow key moves the cursor left as long as the position
    # is not the start of the first line
    elif c == 'l-arr':
        if count != 0:
            count -= 1
            addr = LINE2_START - (0x40 * firstLine) + count
            lcd_out(LCD_CMD, addr)
            
        elif not firstLine:
            count = 15
            firstLine = True
            lcd_out(LCD_CMD, LINE1_END)
        
    
    # down arrow key moves the cursor down from line 1 to line 2
    elif c == 'd-arr':
        if firstLine:
            addr = LINE2_START + count
            firstLine = False
            lcd_out(LCD_CMD, addr)
        
    

    # backspace key behaves like the left arrow key with the addition
    # of clearing the address moved to (or doing nothing if no move was performed)
    # the cursor remains at the cleared address
    elif c == 'bksp':
        if (count == 0) and (not firstLine):
            lcd_out(LCD_CMD, LINE1_END)
            lcd_out(LCD_CHAR, 0x10)
            lcd_out(LCD_CMD, LINE1_END)
            count = 15
            firstLine = True

        elif count != 0:
            count -= 1
            addr = LINE2_START - (0x40 * firstLine) + count
            lcd_out(LCD_CMD, addr)
            lcd_out(LCD_CHAR, 0x10)
            lcd_out(LCD_CMD, addr)
            
    
    # delete key clears the current address and leaves the cursor at that same address
    elif c == 'delete':
        if count != 15:
            lcd_out(LCD_CHAR, 0x10)
            if firstLine:
                lcd_out(LCD_CMD, LINE1_START + count)
            else:
                lcd_out(LCD_CMD, LINE2_START + count)

    
    # home key moves the cursor to the start of the current line
    elif c == 'home':
        if firstLine:
            lcd_out(LCD_CMD, LINE1_START)
        else:
            lcd_out(LCD_CMD, LINE2_START)
        
        count = 0
    


    # end key moves the cursor to the end of the current line
    elif c == 'end':
        if firstLine:
            lcd_out(LCD_CMD, LINE1_END)
        else:
            lcd_out(LCD_CMD, LINE2_END)

        count = 15
    

    # tab key is ignored; all other characters are printed normally
    # printing on the end of a line moves cursor to the start of the other line
    #  i.e. print at end of line1 and cursor moves to start of line2
    #       print at end of line2 and cursor moves to start of line1
    elif c != '\x09':
        if count < 15:
            lcd_out(LCD_CHAR, ord(c))
            count += 1
        
        elif not firstLine:
            lcd_out(LCD_CHAR, ord(c))
            lcd_out(LCD_CMD, LINE1_START)
            count = 0
            firstLine = True
        
        elif firstLine:
            lcd_out(LCD_CHAR, ord(c))
            lcd_out(LCD_CMD, LINE2_START)
            count = 0
            firstLine = False
    
    # return the updated values of firstLine and count
    return [firstLine, count]




def main():
    init()
    
    firstLine = True
    charCount = 0

    while True:
        char = getKey.getKey()
        
        [firstLine, charCount] = writeChar(char, firstLine, charCount)





if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    finally:
        lcd_out(LCD_CMD, 0x01)
        lcd_out(LCD_CMD, 0X0C)
        GPIO.cleanup()
