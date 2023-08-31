import network
import socket
import time
import machine
import urequests as requests
import ujson
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

i2c = I2C(1, scl = Pin(15), sda = Pin(14)) # I2C interface
oled = SSD1306_I2C(128, 64, i2c) # Initialize OLED

wlan = network.WLAN(network.STA_IF)

def connect_wlan(ssid, password): #Connect to WLAN
    count = 15 # duration to establish connection, else failed
    
    oled.fill(0)   
    wlan.active(True)
    wlan.connect(ssid, password)
    while wlan.isconnected() == False:
        oled.text('connecting to', 12, 20)
        oled.text(ssid, 64-len(ssid)*4, 34)
        oled.show()
        time.sleep(1)
        count -= 1
        if count < 0:
            break
    else:
        oled.fill(0)
        oled.text('connected to', 16, 20)
        oled.text(ssid, 64-len(ssid)*4, 34)
        oled.show()
    
    if not wlan.isconnected():
        oled.fill(0)
        oled.text('wlan connection', 4, 20)
        oled.text('failed', 40, 34)
        oled.show()
    
    time.sleep(2)
    #ip = wlan.ifconfig()[0]
    

def connect_kubios(intervals):
    APIKEY = "pbZRUi49X48I56oL1Lq8y8NDjq6rPfzX3AQeNo3a"
    CLIENT_ID = "3pjgjdmamlj759te85icf0lucv"
    CLIENT_SECRET = "111fqsli1eo7mejcrlffbklvftcnfl4keoadrdv1o45vt9pndlef"
    LOGIN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/login"
    TOKEN_URL = "https://kubioscloud.auth.eu-west-1.amazoncognito.com/oauth2/token"
    REDIRECT_URI = "https://analysis.kubioscloud.com/v1/portal/login"
    response = requests.post(
    url = TOKEN_URL,
    data = 'grant_type=client_credentials&client_id={}'.format(CLIENT_ID),
    headers = {'Content-Type':'application/x-www-form-urlencoded'},
    auth = (CLIENT_ID, CLIENT_SECRET))
    response = response.json() #Parse JSON response into a python dictionary
    access_token = response["access_token"] #Parse access token out of the response dictionary
    ##########################################################################################
    #dataset creation HERE
    data_set = {
    "type": "RRI",
    "data": intervals,
    "analysis": {
        "type": "readiness"
        }
    }

    # Make the readiness analysis with the given data
    response = requests.post(
    url = "https://analysis.kubioscloud.com/v2/analytics/analyze",
    headers = { "Authorization": "Bearer {}".format(access_token), #use access token to access your KubiosCloud analysis session
    "X-Api-Key": APIKEY },
    json = data_set) #dataset will be automatically converted to JSON by the urequests library
    response = response.json()
    
    """
    oled.fill(0)
    oled.text("Mean BPM:", 0, 0, 1)
    oled.text(str(response["analysis"]["mean_hr_bpm"]), 0, 10, 1)
    oled.text("PNS:", 0, 20, 1)
    oled.text(str(response["analysis"]["pns_index"]), 0, 30, 1)
    oled.text("SNS:", 0, 40, 1)
    oled.text(str(response["analysis"]["sns_index"]), 0, 50, 1)
    oled.show()
    """
    
    #return response["analysis"]["mean_hr_bpm"], response["analysis"]["stress_index"], response["analysis"]["readiness"]
    return response