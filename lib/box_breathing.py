import time
import ssd1306
from machine import Pin, I2C
from led_loading import LedController

i2c = I2C(1, sda=Pin(14), scl=Pin(15))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

leds = LedController()


def show_message(msg, duration, leds):
        oled.fill_rect(1, 22, 126, 8, 0)
        oled.text(msg, (128 - len(msg) * 8) // 2, 22)
        for count in range(duration, 0, -1):
            oled.fill_rect(1, 36, 126, 8, 0)  # Clear previous countdown number
            oled.text(str(count), 64 - (len(str(count)) * 8) // 2, 36)
            oled.show()
            
            if count == 3:
                leds.all_on()
            elif count == 2:
                leds.led1.off()
            elif count == 1:
                leds.led2.off()
            
            if count != 1:
                time.sleep(1)
            else:
                time.sleep(0.998)  # Adjust the duration for the last number (1) to ensure it is oleded for a full second


def oled_box_breathing(leds):
    oled.fill(0)
    show_message("Get ready", 3, leds)
    
    for i in range(1): # How many sessions

        # Breathe in
        oled.line(0, 0, 127, 0, 1)
        #oled.line(0, 13, 127, 13, 1)
        show_message("Breathe in", 3, leds)

        # Hold breath
        oled.line(127, 0, 127, 63, 1)
        #oled.line(127, 13, 127, 51, 1)
        show_message("Hold breath", 3, leds)

        # Breathe out
        oled.line(0, 63, 127, 63, 1)
        #oled.line(0, 51, 127, 51, 1)
        show_message("Breathe out", 3, leds)

        # Don't breathe
        oled.line(0, 0, 0, 63, 1)
        #oled.line(0, 13, 0, 51, 1)
        show_message("Don't breathe", 3, leds)
    
    leds.all_off()

"""
while True:
    oled_box_breathing(leds)
    leds.all_off()
    time.sleep(5)
"""
