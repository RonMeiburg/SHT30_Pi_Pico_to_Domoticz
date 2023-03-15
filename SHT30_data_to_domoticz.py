import time
import network
import urequests
from machine import Pin, I2C, 

# Parameters for connecting to Wifi
#
SSID        = "YOUR SSID HERE"
PASSWD      = "WAP PASSWORD HERE"
#
# Parameters for sending data to Domoticz
#
WEBURL      = "http://DOMOTICZ_HOST_IP:DOMOTICZ_PORT GOES HERE"
JSON_API    = "/json.htm?type=command&param=udevice&idx="
DOMOTICZ_ID = "DOMOTICZ DEVICE NUMBER GOES HERE"
JSON_PARAMS = "&nvalue=0&svalue="


class SHT30:
    '''
    Minimal functionality to perform reliable single read from SHT30 sensor
    '''

    def __init__(self,i2c) -> None:
        self.i2c  = i2c
        self.temp = 0
        self.hum  = 0
        self.checksum = True
        
    def reset(self) -> None:
        '''
        Send break command (0x3093) followed by
        soft reset (0x30A2) to get sensor in predictable state
        Retry in case of communication error
        '''
        while True:
            try:
                self.i2c.writeto(0x44, b'\x30\x93')
            except:
                blink_signal(led, SENS_NOWRITE)  # Cannot write to sensor, also i2c bus error
                time.sleep(5)
            else:
                time.sleep_ms(10)
                self.i2c.writeto(0x44, b'\x30\xA2')
                time.sleep_ms(10)
                break
        
    def measure(self) -> None:
        '''
        Send command for single measurement with with high repeatability (0x2C06)
        Then collect 6 bytes with temperature, relative humidity and a CRC
        Populate self.temp with temperature in Celsius, self.hum with relative
        humidiy in %, and CRC check with True (==success) or False (==failed)
        '''
        while True:
            try:
                self.i2c.writeto(0x44,b'\x2C\x06')
            except:
                blink_signal(led, SENS_NOWRITE)
                time.sleep(5)
            else:
                break
        time.sleep_ms(100)
        try:
            raw_data = i2c.readfrom(0x44,6)
        except:
            blink_signal(led, SENS_NOREAD)
            self.temp = 0
            self.hum = 0
            self.checksum = False
        else:            
            self.temp = round((((raw_data[0] << 8 |  raw_data[1]) * 175) / 0xFFFF) - 45,1)
            self.hum  = round(((raw_data[3] << 8 | raw_data[4]) * 100.0) / 0xFFFF,1)
            # set the checksum byte. 
            self.check_crc(raw_data)
            if self.checksum == False:
                blink_signal(led, SENS_BADCRC)
        
    def check_crc(self, raw_data) -> None:
        '''
        crc polynomial P(x) = x^8 + x^5 + x^4 + 1 = 100110001 = 0x131
        calculates 8-Bit checksums with given polynomial and compare with crc bytes
        SHT returns TempMSB, TempLSB, TempCRC, HumMSB, HumLSB, HumCRC
        '''
        self.checksum = True
        for i in range(2):
            data = raw_data[i*3:i*3 + 3]
            crc = 0xFF        
            for byte in data[:-1]:
                crc ^= byte
                for _ in range(8, 0, -1):
                    if crc & 0x80:
                        crc = (crc << 1) ^ 0x131
                    else:
                        crc <<= 1
            if data[-1] != crc:
                self.checksum = False
                break
           
def blink_signal(led, signal) -> None:
    length = len(signal)
    for i in range(0,length,2):
        led.value(1)
        time.sleep(signal[i])
        led.value(0)
        if i != length-1:
            time.sleep(signal[i+1])

SUCCESS = [0.5]       # data succesfully recorded and sent
#
# All Webserver related messages start with single 0.2 s led_on
#
WEBS_UNREACHABLE  = [.2,.2,.2,.5,1]  # webserver cannot be reached
WEBS_REJECT =       [.2,.2,.2,.5,.2] # webserver refuses access
#
# All LAN messages start with single 2s led_on.
#
LAN_ERROR =   [2,.5,.2,.2]        # One of several issues with lan access
LAN_WAITING = [2,.5,2]            # No lan connection
LAN_OK =      [2,.5,.5,.5,.5,.5]  # IP received, lan is ok
#
# Sensor messages. Start with two 1 sec flashes
#
SENS_NOWRITE= [1,.2,1,.5,.2,.2]        # Cannot write to sensor, also i2c bus error
SENS_NOREAD = [1,.2,1,.5,.2,1]         # Cannot read data from sensor
SENS_BADCRC = [1,.2,1,.5,2,.2,.2,.2]   # Data received, but bad crc


# define system led. led.value(0) is off, led.value(1) is on
led = Pin("LED", Pin.OUT)
# choose GPIO pin 16 and 17 numbers to connect data and systemcables
sdaPIN = Pin(16)
sclPIN = Pin(17)
# i2cbus = 0 for sda/scl=0/1, 4/5, 8/9 12/13, 16/17 etc
# i2cbus = 1 for sda/scl 2/3, 6/7 etc
i2cbus = 0  
# default freq = 400000. If i2c.write() or i2c.read() produce bus errors,
# or total hangups, try lowering. For DHT30 the frequency is not that critical
i2c    = I2C(i2cbus,sda=sdaPIN, scl=sclPIN, freq=10000)

#initialize the sensorobject and clean state in the sensor
sensor = SHT30(i2c)
sensor.reset()

# set up the network

# STA_IF implies connect to upstream Wifi access point
wlan = network.WLAN(network.STA_IF)
# Fire up the wlan HW
wlan.active(True)

# Connect to the network
wlan.connect(SSID, PASSWD)

while True:
    if wlan.status() in [network.STAT_IDLE,
                         network.STAT_WRONG_PASSWORD,
                         network.STAT_NO_AP_FOUND,
                         network.STAT_CONNECT_FAIL
                         ]:
        blink_signal(led, LAN_ERROR)
    else:
        break
                         
while True:
    if wlan.status() == network.STAT_CONNECTING:
        blink_signal(led, LAN_WAITING)
    elif wlan.status() == network.STAT_GOT_IP:
        blink_signal(led, LAN_OK)
        break
    else:
        blink_signal(led, LAN_ERROR) # Unknown network status

status = wlan.ifconfig()
#print( 'Connected to ' + SSID + '. ' + 'Device IP: ' + status[0] )
    
# we add a simple routine to write data to the Development Domoticz

while True:
    sensor.measure()
    temp = str(sensor.temp)
    hum  = str(sensor.hum)
    print(temp, hum)
    try:
        r=urequests.get(WEBURL + JSON_API + DOMOTICZ_ID + JSON_PARAMS + temp+";"+ hum + ";0")
    except Exception as e:
        blink_signal(led, WEBS_UNREACHABLE)
    else:
        if "OK" not in r.text:
            blink_signal(led, WEBS_REJECT)
        else:
            blink_signal(led, SUCCESS)
        r.close()

    time.sleep(5)


