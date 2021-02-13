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
                    logging.info("Pattern has finished")
                    self.leds.clear()
                    self.leds.refresh()
                    self.generator = None
                    
            sts = self.leds.status()
            if sts:
                logging.info("Received: %s" % sts)

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

    def status(self):
        return {'running': self.generator is not None, 'pattern': self.pattern}


class MyHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super(MyHandler, self).setup()
        self.ledThread = self.server.ledThread

    def handle(self):
        req = self.rfile.readline().strip()
        cmd, pattern, p = json.loads(req)
        logging.info("cmd:%s pattern:%s p:%s" % (cmd,pattern,p))
        if cmd == 'pattern':
            params = Params()
            params.update(p)
            logging.info("Request: %s %s %s" % (cmd, pattern, params))
            pat = ledPatternFactory(pattern, LED_COLUMNS, LED_ROWS)
            self.ledThread.setPattern(pat, params)
        elif cmd == 'status':
            pass
        elif cmd == 'restart':
            self.server.stop()
        elif cmd == 'color':
            self.ledThread.setColor(pat, params)
        elif cmd == 'speed':
            self.ledThread.setSpeed(pat, params)
        elif cmd == 'mode':
            self.ledThread.setMode(pat, params)
        elif cmd == 'brightness':
            self.ledThread.setBrightness(pat, params)
        elif cmd == 'autoCycle':
            self.ledThread.setAutoCycle(pat, params)
        self.wfile.write(bytes(json.dumps(self.ledThread.status())+'\n', encoding='utf-8'))


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
