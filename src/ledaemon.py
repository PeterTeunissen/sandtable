#!/usr/bin/python3
import time
import logging
import json
import socket
import socketserver
from threading import Thread
from importlib import import_module
from ledable import Ledable, ledPatternFactory
from tcpserver import StoppableTCPServer
from dialog import Params
from Sand import LED_DRIVER, LED_ROWS, LED_COLUMNS, LED_MAPPING, LED_PARAMS,\
    LED_HOST, LED_PORT, LED_PERIOD
from ledapi import ledapi

# The specific LED driver is specified in the machine configuration
Leds = import_module('machines.%s' % LED_DRIVER)

class startupPattern(Ledable):
    def __init__(self, cols, rows):
        self.editor = []

    def generator(self, leds, params):
        revCount = 120
        for rev in range(revCount):
            leds.set(0, leds.HSB(720.0*rev/revCount, 100, 50 * rev/revCount), end=len(leds.leds)-1)
            yield True
        yield False


class LedThread(Thread):
    def __init__(self):
        super(LedThread, self).__init__()
        self.leds = Leds.Leds(LED_ROWS, LED_COLUMNS, LED_MAPPING, LED_PARAMS)
        self.leds.refresh()
        self.setPattern(startupPattern(LED_COLUMNS, LED_ROWS), None)
        self.status=None
        self.ledstatus=None
        self.cnt=0

    def run(self):
        self.running = True
        logging.info("LedThread active")
        while self.running:
            if self.generator:
                try:
                    if next(self.generator):
                        self.leds.refresh()
                except (GeneratorExit, StopIteration):
                    # Generator has finished, turn off the lights
                    #logging.info("Pattern has finished")
                    self.leds.clear()
                    self.leds.refresh()
                    self.generator = None
 
            sts = self.leds.status()
            if sts!="":
                # logging.info("ledaemon Received: %s" % sts)
                try:
                    st = sts.decode()
                    # logging.info("Decode done: %s" % st)
                    if st.find("{")!=-1 and st.find("}")!=-1:
                        self.ledstatus = st
                        self.cnt=self.cnt+1
                        # logging.info("Updated ledstatus")
                    else:
                        logging.info("Discarded")
                except:
                    logging.info("Exception caught")

            time.sleep(LED_PERIOD)
        self.leds.close()
        logging.info("LedThread exiting")

    def setPattern(self, pattern, params):
        logging.info("Switching to pattern: %s" % pattern)
        self.pattern = type(pattern).__name__
        self.generator = pattern.generator(self.leds, params)
        if params:
            if params["mode"]>=0:
                self.leds.setMode(params["mode"])

    def stop(self):
        self.running = False

    def updateStatus(self,c):
        while c==self.cnt:
            time.sleep(0.01)

    def setSpeed(self,speed):
        c=self.cnt
        self.leds.setSpeed(speed)
        self.updateStatus(c)

    def setBrightness(self,brightness):
        c=self.cnt
        self.leds.setBrightness(brightness)
        self.updateStatus(c)

    def setMode(self,mode):
        c=self.cnt
        self.leds.setMode(mode)
        self.updateStatus(c)

    def setAutoCycle(self,autocycle):
        c=self.cnt
        self.leds.setAutoCycle(autocycle)
        self.updateStatus(c)

    def setColor(self,color):
        c=self.cnt
        self.leds.setColor(color)
        self.updateStatus(c)

    def getLedstatus(self):
        return self.ledstatus

    def status(self):
        s = {'running': self.generator is not None, 'pattern': self.pattern is not None, 'status': self.status is not None}
        return s

    def handleMqtt(self,msg):
        print("LedThread handleMqtt -> " + msg.topic + " " + str(msg.payload.decode()))


class MyHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super(MyHandler, self).setup()
        self.ledThread = self.server.ledThread

    def handle(self):
        req = self.rfile.readline().strip()
        cmd, pattern, p = json.loads(req)
        logging.info("cmd:%s pattern:%s p:%s" % (cmd,pattern,p))
        if cmd == 'pattern':
            pass
            #params = Params()
            #params.update(p)
            #logging.info("Request: %s %s %s" % (cmd, pattern, params))
            #pat = ledPatternFactory(pattern, LED_COLUMNS, LED_ROWS)
            #self.ledThread.setPattern(pat, params)
        elif cmd == 'status':
            pass
        elif cmd == 'ledstatus':
            self.ledstatus = self.ledThread.getLedstatus()
        elif cmd == 'restart':
            self.server.stop()
        elif cmd == 'color':
            self.ledThread.setColor(pattern)
        elif cmd == 'speed':
            self.ledThread.setSpeed(pattern)
        elif cmd == 'mode':
            self.ledThread.setMode(pattern)
        elif cmd == 'brightness':
            self.ledThread.setBrightness(pattern)
        elif cmd == 'autoCycle':
            self.ledThread.setAutoCycle(pattern)
        self.ledstatus = self.ledThread.getLedstatus()
        s = self.ledstatus
        self.wfile.write(bytes(json.dumps(s), encoding='utf-8'))

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Starting the SandTable ledaemon')

    ledThread = LedThread()
    ledThread.start()

    # Start the socket server and listen for requests
    # Retry logic has been implemented because sometimes sockets don't release quickly
    # FIX: The retry logic should be moved to the socket server itself
    logging.info("Trying to listen on %s:%d" % (LED_HOST, LED_PORT))
    retries = 10
    server = None
    while retries > 0:
        try:
            server = StoppableTCPServer((LED_HOST, LED_PORT), MyHandler)
            logging.info("SocketServer connected")
            break
        except socket.error as e:
            logging.error("%d retries left: %s" % (retries, e))
            retries -= 1
            time.sleep(10.0)
    if server:
        server.ledThread = ledThread
        server.serve()
    logging.info("Out of server loop!")

    ledThread.stop()

    exit(1)
