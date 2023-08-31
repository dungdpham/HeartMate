from fifo import Fifo
from machine import ADC # Generic ADC object
from piotimer import Piotimer as Timer # Rename timer to use Piotimer
#import time


class Recorder:
    def __init__(self, fs=250):# Sampling frequency (= samples per second)
        self.adc = ADC(26)
        self.fs = fs
        self.fifo = Fifo(2*self.fs)
        self.timer = Timer(freq=self.fs, callback=self.adc_read)
        #self.reset()

    def adc_read(self, tim):#Data acquisition handler
        x = self.adc.read_u16()
        self.fifo.put(x)
        
    def get(self):
        return self.fifo.get()
    
    def empty(self):
        return self.fifo.empty()

    def stop_timer(self): #stop timer
        self.timer.deinit()
        
        
