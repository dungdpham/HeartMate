from machine import Pin
import utime
from led import Led

class LedController:
    def __init__(self, pico_led_pin='LED', led1_pin=22, led2_pin=21, led3_pin=20, short_sleep=0.1, long_sleep=0.3, brightness = 5):
        self.pico_led = Pin(pico_led_pin, Pin.OUT)
        self.led1 = Led(led1_pin)
        self.led2 = Led(led2_pin)
        self.led3 = Led(led3_pin)
        
        self.led1.brightness(brightness)
        self.led2.brightness(brightness)
        self.led3.brightness(brightness)
        
        self.short_sleep = short_sleep
        self.long_sleep = long_sleep
        self.leds = [self.led1, self.led2, self.led3]

    def run(self):
        while True:
            for current_led in self.leds:
                self.pico_led.value(1)
                current_led.value(1)
                utime.sleep(self.short_sleep)
                self.pico_led.toggle()
                utime.sleep(self.long_sleep)
                current_led.value(0)

    def all_off(self):
        for current_led in self.leds:
            current_led.off()
 
    
    def all_on(self):
        for current_led in self.leds:
            current_led.on()
            
"""           
if __name__ == "__main__":
    led_controller = LedController()
    led_controller.all_off()
"""
