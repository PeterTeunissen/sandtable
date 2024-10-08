import board
import neopixel
from LedsBase import LedsBase
import serial
import time
from Sand import LED_PARAMS
import logging
from time import sleep
import requests
import logging

class Leds(LedsBase):
    """Communicate with a ESP8266 based WS2812Fx lighting system"""

    mode = LED_PARAMS["mode"]
    sts = None

    def __init__(self, rows, cols, mapping, params):
        self.mapping = mapping
        LedsBase.__init__(self, rows, cols)
        self.mode = LED_PARAMS["mode"]
        self.sts = None

    def newstatus(self):
        if (self.mode == "serial"):
            while self.ser.in_waiting==0:
                sleep(0.100)

            if self.ser.in_waiting > 0:
                line = self.ser.readline()
                return line
        if self.sts is None:
            self.sendHttp("r","")
        logging.info("newStatus call returning %s" % self.sts.content)
        return self.sts.content

    def status(self):
        if (self.mode == "serial"):
            if self.ser.in_waiting > 0:
                line = self.ser.readline()
                return line
        if self.sts is None:
            self.sendHttp("r","")
        # logging.info("status call returning %s" % self.sts.content)
        return self.sts.content

    def flushIn(self):
        if (self.mode == "serial"):
            while self.ser.in_waiting>0:
                self.ser.readline()

    def sendHttp(self,command,arg):
        httpReq = "http://" + LED_PARAMS["esp_ip"] + "/set?" + command + "=" + arg
        logging.info("Make http request to %s command %s arg %s" % (httpReq,command,arg)) 
        self.sts = requests.get(httpReq)
        logging.info("http result: %d body %s" % (self.sts.status_code,self.sts.content))

    def sendSerial(self,c):
        if (self.mode == "serial"):
            self.flushIn()
            logging.info("Sending serial light command: %s", c)
            self.ser.write(bytes('{'+c+'}'+'\n', encoding='UTF-8'))

    def sendTime(self):
        tzoff = time.localtime().tm_gmtoff
        self.sendSerial("t"+str(int(time.time())+tzoff))

    def connect(self):
        if (self.mode == "serial"):
            self.ser = serial.Serial(LED_PARAMS["port"], LED_PARAMS["baud"], timeout=1)
            logging.info("Connected to USB1")
        #self.sendSerial("r")
        #self.sendSerial("r")
        # self.sendTime()a
        if (self.mode != "serial"):
            self.sendHttp("r","")
            logging.info("Send http r command")

    def refresh(self):
        pass

    def disconnect(self):
        logging.info("Connecting from USB1")
        del self.ser

    def setColor(self, rgb):
        #print("RGB value:",rgb)
        #red = rgb[0]
        #green = rgb[1]
        #blue = rgb[2]
        #print("RGB values:",red, green, blue)
        #rgbInt = (red<<16) + (green<<8) + blue
        #self.sendSerial("c"+str(rgbInt))
        logging.info("Setting color: %s",rgb)
        self.sendHttp("c",str(rgb))
        #self.sendSerial("c"+str(rgb))

    def setMode(self,mode):
        logging.info("Mode value: %s",mode)
        #self.sendSerial("m"+str(mode))
        self.sendHttp("m",str(mode))

    def setAutoCycle(self,cycle):
        logging.info("Cycle value: %s",cycle)
        if cycle==False or cycle=="False":
            self.sendHttp("a","-")
            #self.sendSerial("a-")
        if cycle==True or cycle=="True":
            self.sendHttp("a","+")
            #self.sendSerial("a+")

    def setBrightness(self,brightness):
        logging.info("Brightness value: %s",brightness)
        #self.sendSerial("b"+str(brightness))
        self.sendHttp("b",str(brightness))

    def setSpeed(self,speed):
        logging.info("Speed value: %s",speed)
        #self.sendSerial("s"+str(speed))
        self.sendHttp("s",str(speed))
