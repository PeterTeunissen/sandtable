import board
import neopixel
from LedsBase import LedsBase
import serial
import time
from Sand import LED_PARAMS
import logging
from time import sleep

class Leds(LedsBase):
    """Communicate with a ESP8266 based WS2812Fx lighting system"""

    def __init__(self, rows, cols, mapping, params):
        self.mapping = mapping
        LedsBase.__init__(self, rows, cols)

    def newstatus(self):
        while self.ser.in_waiting==0:
            sleep(0.100)
            
        if self.ser.in_waiting > 0:
            line = self.ser.readline()
            return line
        return ""

    def status(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline()
            return line
        return ""

    def flushIn(self):
        while self.ser.in_waiting>0:
            self.ser.readline()

    def sendSerial(self,c):
        self.flushIn()
        print("Sending light command:", c)
        self.ser.write(bytes('{'+c+'}'+'\n', encoding='UTF-8'))
        
    def sendTime(self):
        tzoff = time.localtime().tm_gmtoff
        self.sendSerial("t"+str(int(time.time())+tzoff))

    def connect(self):
        self.ser = serial.Serial(LED_PARAMS["port"], LED_PARAMS["baud"], timeout=1)
        print("Connected to USB1")
        self.sendSerial("r")
        self.sendSerial("r")
        self.sendTime()

    def refresh(self):
        pass

    def disconnect(self):
        print("Connecting from USB1")
        del self.ser

    def setColor(self, rgb):
        #print("RGB value:",rgb)
        #red = rgb[0]
        #green = rgb[1]
        #blue = rgb[2]
        #print("RGB values:",red, green, blue)
        #rgbInt = (red<<16) + (green<<8) + blue
        #self.sendSerial("c"+str(rgbInt))
        self.sendSerial("c"+str(rgb))

    def setMode(self,mode):
        print("Mode value:",mode)
        self.sendSerial("m"+str(mode))

    def setAutoCycle(self,cycle):
        print("Cycle value:",cycle)
        if (cycle==False):
            self.sendSerial("a-")
        if (cycle==True):
            self.sendSerial("a+")

    def setBrightness(self,brightness):
        print("Brightness value:",brightness)
        self.sendSerial("b"+str(brightness))

    def setSpeed(self,speed):
        print("Speed value:",speed)
        self.sendSerial("s"+str(speed))
