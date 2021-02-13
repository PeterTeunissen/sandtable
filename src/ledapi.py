from Sand import LED_HOST, LED_PORT
import socket
import json


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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.hostName, self.hostPort))
            j = json.dumps((cmd, pattern, params))
            print("Sending to socket:",j)
            sock.sendall(bytes(json.dumps((cmd, pattern, params))+'\n', encoding='utf-8'))
            self._status = json.loads(sock.recv(512).decode('utf-8'))
        return self._status

    def setMode(self, mode):
        return self.command('mode', mode)

    def setSpeed(self, speed):
        return self.command('speed', speed)

    def setAutoCycle(self, autoCycle):
        return self.command('autoCycle', autoCycle)

    def setBrightness(self, brightness):
        return self.command('brightness', brightness)

    def setColor(self, color):
        return self.command('color', color)

    def setPattern(self, pattern, params):
        return self.command('pattern', pattern, params)

    def status(self):
        return self.command('status')

    def restart(self):
        return self.command('restart')
