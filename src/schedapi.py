import socket
import json
from Sand import SCHEDULER_HOST, SCHEDULER_PORT
import logging

class JobInfo():
    def __init__(self,id,name,functionName,trigger,params):
        self.id=id
        self.name=name
        self.functionName=functionName
        self.params=params
        self.trigger=trigger

    def __enter__(self):
        return self

    def toJSON(self):
        js = json.dumps(self, default=lambda o: o.__dict__)
        return js
        
    def getTrigger(self):
        return self.trigger
        
    def getName(self):
        return self.name
        
    def getID(self):
        return self.id
        
    def getFunctionName(self):
        return self.functionName
        
    def getParams(self):
        return self.params

class TriggerInfo():
    def __init__(self,year,month,day,week,day_of_week,hour,minute,second):
        self.year=year
        self.month=month
        self.day=day
        self.week=week
        self.day_of_week=day_of_week
        self.hour=hour
        self.minute=minute
        self.second=second
        
    def __enter__(self):
        return self

    def toJSON(self):
        js = json.dumps(self, default=lambda o: o.__dict__)
        return js        

class schedapi():
    def __init__(self, hostName=SCHEDULER_HOST, portNumber=SCHEDULER_PORT):
        self.hostName = hostName
        self.portNumber = portNumber
        self.BUFFER_SIZE = 2048
        self._status = None

    def __enter__(self):
        return self

    def __exit__(self, e, t, tb):
        return False

    def command(self, command, data=None):
        logging.info("schedapi command: %s" % command)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.hostName, self.portNumber))
            sock.sendall(bytes(json.dumps((command, data))+'\n', encoding='utf-8'))
            resp = sock.recv(self.BUFFER_SIZE).decode('utf-8')
            self._status = json.loads(resp)

    def demoOnce(self):
        self.command("demoOnce")

    def demoContinuous(self):
        self.command("demoContinuous")

    def demoHalt(self):
        self.command("demoHalt")

    def runJob(self,data):
        self.command("jobRun",data)

    def addJob(self,data):
        self.command("jobAdd",data)

    def deleteJob(self,data):
        self.command("jobDelete",data)

    def listJobs(self):
        self.command("jobList")

    def getJobs(self):
        self.listJobs()
        return self._status['jobs']
                
    def status(self):
        self.command("status")
        return self._status

    def restart(self):
        self.command("restart")
