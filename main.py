"""
Metropolia University of Applied Sciences

Hardware 1+2 Project
TXL22S1-A Group 106:
Arijana Määttä
Adrian Garcia Castro
Hanh Hoang
Dung Pham

Project teacher:
Sakari Lukkarinen
"""

# Setup
# This setting is used for showing runtime error messages
import micropython
micropython.alloc_emergency_exception_buf(100)

# System modules and libraries
from ssd1306 import SSD1306_I2C # I2C driver interface for OLED
from machine import Pin, I2C, Timer # Generic Pin and I2C object
import framebuf # Frame Buffer
from led import Led # Use dimmabled LEDs
#from utime import sleep_ms # Used for waiting interactions from user
import time
import network


# Custom modules
from livefilter import LiveSosFilter # Real-time filtering implementation
from recorder_value import Recorder # Record class
from heartratecalculation import Hrv # Algorithm and analysis class
from graphic import Graphic, logo, derp # Drawing
from credits_sliding import credits_sliding # Credits sliding animation
from KubiosCloud import connect_wlan, connect_kubios # Wlan connection and Kubios API
from led_loading import LedController # Class for led control
from box_breathing import oled_box_breathing # Box breathing function


# Hardware settings
fs = 250 # Sampling frequency (= samples per second)
N = fs // 25 # Display every Nth sample

i2c = I2C(1, scl = Pin(15), sda = Pin(14)) # I2C interface
oled = SSD1306_I2C(128, 64, i2c) # Initialize OLED

wlan = network.WLAN(network.STA_IF) # Wlan
ssid = 'kmd758group6'
password = 'our_group_is_6'


# Set up button interrupts
rot_Push = Pin(12, Pin.IN, Pin.PULL_UP) # Initialize Rotary push button
debounce_push = 0
def rot_push(Pin):
    global debounce_push, menu
    if time.ticks_ms() - debounce_push > 300:
        if menu == 0 and cursor == 0: # select Credits
            menu = -1
        elif menu == 0 and cursor == 2: # select Box breathing
            menu = 6
        elif menu == 6: # route Box breathing to continue to normal path after taking measurements
            menu = 2
        else:
            menu += 1
        
        if menu == 5: # go back to start screen after Kubios report
            menu = 0
        debounce_push = time.ticks_ms()
rot_Push.irq(handler = rot_push, trigger = Pin.IRQ_RISING)


rota = Pin(10, Pin.IN, Pin.PULL_UP) # Rotary turn
rotb = Pin(11, Pin.IN, Pin.PULL_UP)
debounce_turn = 0
def rot_turn(Pin):
    global cursor, row, debounce_turn
    if time.ticks_ms() - debounce_turn > 150:
        if menu == 0: # turn to choose options in start screen
            if rotb.value() == 1:
                cursor = min(cursor+1, 2)
            else:
                cursor = max(cursor-1, 0)
                
        if menu == 4: # turn to switching between pages in Kubios report screen
            if rotb.value()==1:
                row = min(row+70, 0)
            else:
                row = max(row-70, -70)
        
        debounce_turn = time.ticks_ms()
rota.irq(handler = rot_turn, trigger = Pin.IRQ_RISING)


# Initialize objects
sosfilter = LiveSosFilter() # Initialize the real-time filter
recorder = Recorder() 
hrv = Hrv()
draw = Graphic(oled)
leds = LedController()


# Declare global variables
count = 0 # Counts how many samples are handled
#L = 20 # Length of the data collection in seconds

x0 = 33100 # Initial average value for x
a = 4/fs # Weight parameter for moving average, about 1/4 of a second

duration = 0 # Time elapsed in second

menu = 0 # 0=Start screen, 1=Measuring screen, 2=Stop measuring, 3=Report, 4=Kubios report, 6=Box breathing, -1=Credits screen
cursor = 1 # Cursor for options on menu 0, 0=1st option, 1=2nd option, 2=3rd option
row = 0 # y-axis position on oled for scrolling in Kubios report

response = {} # placeholder for response from Kubios


#####################################################################
# Functions #########################################################

def start_screen():
    oled.fill(0)
    fb = framebuf.FrameBuffer(logo, 32, 32, framebuf.MONO_HLSB)
    oled.blit(fb, 8, 0)
    oled.text('HEARTMATE', 44, 12, 1)
    
    # Menu layout, comment out 1 of 2 options ##################
    
    # comment out from this line ##############################
    
    # List menu
    oled.text('start now', 42, 32, 1)
    oled.text('breathe 1st', 28, 48, 1)
    
    if cursor == 0:
        oled.fill_rect(120, 11, 8, 8, 1)
    elif cursor == 1:
        oled.fill_rect(120, 32, 8, 8, 1)
    else:
        oled.fill_rect(120, 47, 8, 8, 1)
    oled.show()
    
    """# comment out from this line ##############################
    
    # Line menu
    oled.text('ready?', 44, 30)
    
    if cursor == 1:
        oled.fill_rect(0, 44, 127, 10, 1)
        oled.text('yes, start now', 8, 45, 0)
        
    while menu == 0 and cursor == 2:
        for i in range(-20, 112, 1):
            oled.fill_rect(0, 44, 127, 10, 1)
            oled.text('breathing exercise then start', -i, 45, 0)
            oled.show()
            if menu != 0 or cursor != 2:
                break
        time.sleep(0.2)
        
    while menu == 0 and cursor == 0:
        for i in range(-20, 70, 1):
            oled.fill_rect(0, 44, 127, 10, 1)
            oled.text('maybe see credits first?', -i, 45, 0)
            oled.show()
            if menu != 0 or cursor != 0:
                break
        time.sleep(0.2)
    oled.show()
    
    """# comment out from this line ##############################
    
    leds.all_off()
    leds.leds[cursor].on()


def info():
    credits_sliding(oled)


def main_loop():
    global count, x0
    
    if not recorder.empty():
        count += 1
        
        x = recorder.get()
        x0 = (1-a)*x0 + a*x # Calculate moving average
        y = sosfilter.process(x - x0) # Filter the last data sample

        peak = hrv.detect(y, count)
        
        draw.show_bpm(peak, hrv.BPM)
        draw.beating_heart(peak, count)
        
        draw.graph(y, count)


def stop_screen():
    #oled.fill(0)
    while menu == 2:
        for i in range(-20, 70):
            oled.fill_rect(0, 56, 128, 8, 0)
            oled.text('preliminary report ready', -i,  56)
            oled.show()
            if menu != 2:
                break
        time.sleep(0.3)
    #pass


def report_screen():
    oled.fill(0)
    #bpm = hrv.BPM
    oled.text(f'duration: {duration//60}m{duration%60:02d}s', 0, 0)
    #oled.text(f'count: {str(count)}', 0, 20)
    
    if hrv.analysis() == 0:
        oled.text('no peak found', 0, 14)
    else:
        oled.text(f'avg bpm: {hrv.analysis()[1]:.2f}', 0, 14)
        oled.text(f'mean rr: {hrv.analysis()[0]:.0f} ms', 0, 28)
        oled.text(f'rmssd: {hrv.analysis()[2]:.2f} ms', 0, 42)
    
    while menu == 3:
        for i in range(-20, 78):
            oled.fill_rect(0, 56, 128, 8, 0)
            oled.text('press for Kubios analysis', -i,  56)
            oled.show()
            if menu != 3:
                break
        time.sleep(0.3)
    
    #oled.show()


kubios_request = False
def ask_kubios():
    global response, kubios_request, row
    if not kubios_request:
        oled.fill(0)
        oled.text('fetching report', 4, 14)
        oled.text('from', 48, 28)
        oled.text('Kubios Cloud', 16, 42)
        oled.show()
        
        response = connect_kubios(hrv.ppi_list)
        print(response)
        kubios_request = True
        
    while menu == 4 and response['status'] == 'error':
        
        """# No meme ######################################
        for i in range(-20, 128):
            oled.fill(0)
            oled.text('error', 44, 14)
            oled.text(response['error'], -i, 28)
            oled.show()
            if menu != 4:
                break
        time.sleep(0.3)
        """################################################
        
        # Yes meme #####################################
        oled.fill(0)
        fb = framebuf.FrameBuffer(derp, 49, 53, framebuf.MONO_HLSB)
        oled.blit(fb, 38, 0)
        oled.text('okay!', 90, 3)
        for i in range (-20, 124, 1):
            oled.fill_rect(0, 56, 128, 8, 0)
            oled.text(response['error'], -i, 56)
            oled.show()
            if menu != 4:
                break
        time.sleep(0.3)
        ################################################
        
    if response['status'] == 'ok':
        oled.fill(0)
        oled.text(f'mean BPM: {response["analysis"]["mean_hr_bpm"]:.2f}', 0, row)
        oled.text(f'pns index: {response["analysis"]["pns_index"]:.2f}', 0, row+14)
        oled.text(f'sns index: {response["analysis"]["sns_index"]:.2f}', 0, row+28)
        oled.text(f'stress in.: {response["analysis"]["stress_index"]:.2f}', 0, row+42)
        oled.text(f'readiness: {response["analysis"]["readiness"]:.2f}', 0, row+56)
        oled.text(f'mean rr: {response["analysis"]["mean_rr_ms"]:.0f} ms', 0, row+70)
        oled.text(f'rmssd: {response["analysis"]["rmssd_ms"]:.2f} ms', 0, row+84)
        oled.text(f'sdnn: {response["analysis"]["sdnn_ms"]:.2f} ms', 0, row+98)
        oled.text(f'sd1: {response["analysis"]["sd1_ms"]:.2f} ms', 0, row+112)
        oled.text(f'sd2: {response["analysis"]["sd2_ms"]:.2f} ms', 0, row+126)
        oled.show()


def breathe_1st():
    oled_box_breathing(leds)
    leds.leds[cursor].on()


def second_elapsed(stopwatch):
    global duration
    duration += 1
    #oled.fill_rect(88, 0, 40, 10, 0)
    #oled.text(f'{duration//60}m{duration%60:02d}s', 88, 1)
    draw.show_time(duration)
#stopwatch = Timer(period = 1000, callback = second_elapsed)


#####################################################################
# MAIN ##############################################################

if not wlan.isconnected():
    connect_wlan(ssid, password)
#wlan.deinit() # turn off wlan connection if needed


while True:
    if menu == 0:
        #print(menu)
        start_screen()
        
    elif menu == 1:
        oled.fill(0)
        
        del recorder, hrv, draw # Deletes objects from previous run
        
        # Create new objects
        recorder = Recorder() 
        hrv = Hrv()
        draw = Graphic(oled)
        
        # Reset global values
        count = 0
        x0 = 33100
        duration = 0
        
        kubios_request = False
        row = 0
        
        draw.clear_graph() # Clear old graph
        
        stopwatch = Timer(period = 1000, callback = second_elapsed) # Reinitialize stopwatch
        oled.text(f'0m00s', 88, 1)
        
        while menu == 1:
            main_loop()
            
    elif menu == 2:
        #print(menu)

        recorder.stop_timer() # Stop recorder timer
        stopwatch.deinit() # Stop stopwatch timer
        
        stop_screen()
        
    elif menu == 3:
        #print(menu)
        report_screen()
        
        #print(hrv.ppi_list) # Only for testing, checking validity of ppi_list
        
    elif menu == 4:
        if wlan.isconnected():
            ask_kubios()
        else:
            oled.fill(0)
            oled.text('no wlan', 36, 20)
            oled.text('connection', 24, 34)
            oled.show()
    
    elif menu == 6:
        breathe_1st()
        
        oled.fill(0)
        
        del recorder, hrv, draw # Deletes objects from previous run
        
        # Create new objects
        recorder = Recorder() 
        hrv = Hrv()
        draw = Graphic(oled)
        
        # Reset global values
        count = 0
        x0 = 33100
        duration = 0
        
        kubios_request = False
        row = 0
        
        draw.clear_graph() # Clear old graph
        
        stopwatch = Timer(period = 1000, callback = second_elapsed) # Reinitialize stopwatch
        oled.text(f'0m00s', 88, 1)
        
        while menu == 6:
            main_loop()
    
    elif menu == -1:
        #print(menu)
        info()
    
    #time.sleep(0.1)