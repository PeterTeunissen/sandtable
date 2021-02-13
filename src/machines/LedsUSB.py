import board
import neopixel
from LedsBase import LedsBase
import serial
import time

class Leds(LedsBase):
    """Communicate with a ESP8266 based WS2812Fx lighting system"""

    def __init__(self, rows, cols, mapping, params):
        self.mapping = mapping
        LedsBase.__init__(self, rows, cols)

    def sendSerial(self,c):
        print("Sending light command:", c)
        self.ser.write(("{"+c+"}\n").encode())

    def sendTime(self):
        self.sendSerial("{t"+str(int(time.time()))+"}")

    def connect(self):
        self.ser = serial.Serial('/dev/ttyUSB1', 74880, timeout=1)
        print("Connected to USB1")
        self.ser.write(("").encode())
        self.ser.write(("").encode())
        self.sendTime()
        
    def refresh(self):
        pass

    def status(self):
        if self.ser.in_waiting > 0:
            line = self.ser.readline()
            return line
        return ""

    def disconnect(self):
        print("Connecting from USB1")
        del self.ser
        
    def setColor(self, rgb):
        #print("RGB value:",rgb)
        red = rgb[0]
        green = rgb[1]
        blue = rgb[2]
        print("RGB values:",red, green, blue)
        rgbInt = (red<<16) + (green<<8) + blue
        self.sendSerial("c"+str(rgbInt))        

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
