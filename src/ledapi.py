from Sand import LED_HOST, LED_PORT
import socket
import json
import logging

class ledapi():
    def __init__(self, hostName=LED_HOST, hostPort=LED_PORT):
        self.hostName = hostName
        self.hostPort = hostPort
        self._status = None

    def __enter__(self):
        return self

    def __exit__(self, e, t, tb):
        return False

    def command(self, cmd, pattern=None, params=None):
        logging.info("ledapi sending socket command cmd %s" % cmd)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.hostName, self.hostPort))
            sock.sendall(bytes(json.dumps((cmd, pattern, params))+'\n', encoding='utf-8'))
            resp = sock.recv(2048).decode('utf-8')
            self._status = resp
            logging.info("ledapi: received: %s" % resp)
            self.js = json.loads(json.loads(self._status))
        return self._status

    def setMode(self, mode):
        return self.command('mode', mode)

    def setSpeed(self, speed):
        return self.command('speed', speed)

    def setAutoCycle(self, autoCycle):
        return self.command('autoCycle', autoCycle)

    def setBrightness(self, brightness):
        return self.command('brightness', brightness)

    def setColor(self, rgb):
        rgb=rgb.replace('#','0x')
        i = int(rgb,0)
        return self.command('color', i)

    def getLedstatus(self):
        return self.command('ledstatus')

    def getMode(self):
        self.getLedstatus()
        return self.js["mode"]

    def getAutoCycle(self):
        self.getLedstatus()
        return True if self.js["autocycle"]=="on" else False

    def getColor(self):
        self.getLedstatus()
        c=self.js["color"]
        b=c & 0xFF
        c=c>>8
        g=c & 0xFF
        c=c>>8
        r=c & 0xFF
        print("RGB values:",r, g, b)
        return (r,g,b)

    def getBrightness(self):
        self.getLedstatus()
        return self.js["brightness"]

    def getSpeed(self):
        self.getLedstatus()
        return self.js["speed"]

    def setPattern(self, pattern, params):
        if 'color' in params:
            self.setColor(params['color'])
        if 'brightness' in params:
            self.setBrightness(params['brightness'])
        if 'mode' in params:
            self.setMode(params['mode'])
        if 'speed' in params:
            self.setSpeed(params['speed'])
        if 'autocyle' in params:
            self.setAutocycle(params['autocycle'])
        return self.status()

    def status(self):
        return self.command('status')

    def restart(self):
        pass
        #return self.command('restart')
