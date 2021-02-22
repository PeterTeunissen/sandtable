#!/usr/bin/python3 -u
from pytz import utc
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import time
from datetime import datetime
import logging
import json
import socket
import socketserver
from tcpserver import StoppableTCPServer
from threading import Thread
from collections import deque
import random
from pprint import pprint

from Sand import DATA_PATH, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS,\
   MACHINE_UNITS, MACHINE_ACCEL, MACHINE_FEED,\
   SCHEDULER_ENABLE, SCHEDULER_HOST, SCHEDULER_PORT, drawers,\
   LED_COLUMNS, LED_ROWS
from sandable import sandableFactory
from dialog import Params
from Chains import Chains
from history import History
import board
import digitalio
import mach
from ledable import ledPatternFactory
import ledapi
from schedapi import JobInfo, TriggerInfo

# Parameters
POLLING_DELAY = 0.100     # 1/10 second
DRAW_TIME_MIN = 18        # 18 Seconds
DRAW_TIME_MAX = 25*60     # 25 minutes
PROX_SWITCH_SECS = 8         # Number of seconds to wait for taps

PROX_PIN = board.D18
PROX_PIN.direction = digitalio.Direction.INPUT

# Advanced job scheduler setup

jobstores = {
    'default': SQLAlchemyJobStore(url='sqlite:///%sjobs.sqlite' % DATA_PATH)
}
executors = {
    'default': ThreadPoolExecutor(20),
    'processpool': ProcessPoolExecutor(5)
}
job_defaults = {
    'coalesce': True,
    'max_instances': 3
}

#
# Job actions:
#   "demo"   Run a single demo
#   "method" Draw a specific method
#   "saved"  Draw a saved drawing
#
# Job frequency:
#   "yearly" Run at a specific time and date of the year
#       Data is Hour, Minute, Month, Day
#   "daily" Run at a specific time of the day
#       Data is Hour, Minute
#   "frequency" Run at a specific frequency recurring forever
#       Data is Type (DayOfWeek,Month,Day,Year), Value, Hour, Minute


def JobDemo():
    jobHanlder.demoOnce()


class JobHandler(Thread):
    DIE, QUIET, HALT, RUNNING = -1, 0, 1, 2

    def __init__(self, pause=30):
        super(JobHandler, self).__init__()
        self._state = self.QUIET
        self._count = 0
        self._pause = pause

    def run(self):
        logging.info("JobHanlder active")
        while self._state != self.DIE:
            if self._state == self.QUIET:
                time.sleep(POLLING_DELAY)

            elif self._state == self.RUNNING:
                self._lightsRandom()
                while self._state == self.RUNNING and self._count != 0:
                    self._count -= 1
                    self._drawRandom()
                    self._drawWait()
                    end = time.time() + self._pause
                    while self._state == self.RUNNING and time.time() < end:
                        time.sleep(POLLING_DELAY)
                self._lightsOff()
                if self._state == self.RUNNING:
                    self._state = self.QUIET

            if self._state == self.HALT:
                self._lightsOff()
                self._drawHalt()
                self._state = self.QUIET
        logging.info("JobHandler exiting")

    def demoContinuous(self, count=-1):
        logging.info("demoContinuous(%d) has been called" % count)
        self._count = count
        self._state = self.RUNNING

    def demoOnce(self):
        self.demoContinuous(1)

    def demoHalt(self):
        logging.info("demoHalt has been called")
        if self._state == self.RUNNING:
            self._state = self.HALT

    def proxCallback(self, taps):
        if taps == 2:
            self._lightsRandom()
        elif taps == 3:
            self.demoOnce()
        elif taps == 4:
            self.demoContinuous()
        elif taps == 5:
            self.demoHalt()
        else:
            logging.info("Number of taps: %d" % taps)

    def stop(self):
        self._state = self.DIE

    def _lightsRandom(self):
        pattern = ledPatternFactory('RandomLights', LED_COLUMNS, LED_ROWS)
        params = Params(pattern.editor)
        params['minutes'] = 2.0
        with ledapi.ledapi() as led:
            led.setPattern('RandomLights', params)

    def _lightsOff(self):
        pattern = ledPatternFactory('Off', LED_COLUMNS, LED_ROWS)
        params = Params(pattern.editor)
        with ledapi.ledapi() as led:
            led.setPattern('Off', params)

    def _drawRandom(self):
        boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
        while True:
            if self._state == self.HALT:
                return
            drawer = drawers[random.randint(0, len(drawers)-1)]
            sand = sandableFactory(drawer, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
            params = Params(sand.editor)
            params.randomize(sand.editor)
            try:
                chains = sand.generate(params)
                pchains = Chains.convertUnits(chains, TABLE_UNITS, MACHINE_UNITS)
                pchains = Chains.bound(chains, boundingBox)
                t, d, p = Chains.estimateMachiningTime(pchains, MACHINE_FEED, MACHINE_ACCEL)
                if DRAW_TIME_MIN <= t <= DRAW_TIME_MAX:
                    break
                logging.info("Tried %s but time was %d:%02d" % (sand, int(t/60), int(t) % 60))
            except Exception as e:
                logging.warning("Tried %s but failed with %s" % (sand, e))

        logging.info("Drawing %s, estimated time %d:%02d" % (sand, int(t/60), int(t) % 60))
        History.save(params, drawer, chains, "lastdemo")
        with mach.mach() as e:
            e.run(chains, boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS)

    def _drawWait(self):
        with mach.mach() as e:
            while self._state == self.RUNNING and not e.getStatus()['ready']:
                time.sleep(POLLING_DELAY)

    def _drawHalt(self):
        with mach.mach() as e:
            e.stop()

    def handleJob(self,data):
        logging.info("LedThread handlejob")

class SchedulerSocketHandler(socketserver.StreamRequestHandler):
    def setup(self):
        super(SchedulerSocketHandler, self).setup()
        self.jobHandler = self.server.jobHandler
        self.scheduler = self.server.scheduler

    def handle(self):
        req = self.rfile.readline().strip()
        command, data = json.loads(req)
        logging.info("SchedulerSocketHandler.handle Command: %s, Params: %s" % (command, data))
        if command == 'status':
            pass
        elif command == 'demoOnce':
            self.jobHandler.demoOnce()
        elif command == 'demoContinuous':
            self.jobHandler.demoContinuous()
        elif command == 'demoHalt':
            self.jobHandler.demoHalt()
        elif command == 'restart':
            self._restart()
        elif command == 'jobRun':
            self._jobRun(data)
        elif command == 'jobAdd':
            self._jobAdd(data)
        elif command == 'jobDelete':
            self._deleteJob(data)
        elif command == 'jobList':
            self._listJobs(data)
        else:
            logging.warning("Unknown command: %s" % command)
        resp = json.dumps({'state': self.jobHandler._state , 'jobs': self._listJobs(None)})
        self.wfile.write(bytes(resp, encoding='utf-8'))

    def _restart(self):
        self.server.stop()

    def _listJobs(self,data):        
        js = []
        for job in scheduler.get_jobs():
            j = {}
            j['id']=job.id
            j['name']=job.name
            j['function']=getattr(job.func, '__name__', repr(job.func))
            j['args']=job.args
            j['trigger']=str(job.trigger)
            j['next_run_time']=str(job.next_run_time)
            js.append(j)
        return js
        
    def _deleteJob(self,data):
        for job in self.scheduler.get_jobs():
            if job.id==data['id']:
                logging.info("Deleting Job: %s" % job.id)
                job.remove()
        
    def handleMe(self,data):
        logging.info("socket handleme")

    def _jobRun(self,data):
        for job in self.scheduler.get_jobs():
            if job.id==data['id']:
                logging.info("Running Job: %s" % job.id)
                job.modify(next_run_time=datetime.utcnow())

    def _jobAdd(self,data):
        p = {
          "job": data['job'],
          "params": data['params']
        }
        job = self.scheduler.add_job(self.server.cb, name=data['name'], args=[p], trigger=CronTrigger.from_crontab(data['cron']))
        logging.info("New jobid %s" % job.id)

if __name__ == "__main__":
    logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)
    logging.info('Starting the SandTable scheduler daemon')

    jobHandler = JobHandler()
    jobHandler.start()

    # Start the background job scheduler (which potentially means start servicing jobs)
    scheduler = BackgroundScheduler(jobstores=jobstores, executors=executors, job_defaults=job_defaults, timezone=utc)
    scheduler.start()

    # FIX: Kluge to clear out the scheduler and start a random drawing everyday at 3:00 am.
    #def kluge():
    #    logging.info("Kluge triggered")
    #    if SCHEDULER_ENABLE:
    #        logging.info("Running single demo")
    #        demo.demoOnce()
    #    else:
    #        logging.info("Schedule is disabled")
    #    logging.info("Kluge returned")

    def handleJob(data):
        logging.info("Job triggerd: %s" % data['job'])
        if data['job']=='lightsOn':
            with ledapi.ledapi() as led:
                led.setBrightness(200)
        if data['job']=='lightsOff':
            with ledapi.ledapi() as led:
                led.setBrightness(0)
        if data['job']=='GCode':
            boundingBox = [(0.0, 0.0), (TABLE_WIDTH, TABLE_LENGTH)]
            sand = sandableFactory("GCode", TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS)
            params = Params(sand.editor)
            params['filename']=data['params']
            try:
                chains = sand.generate(params)
                History.save(params, "GCode", chains, "lastdemo")
                with mach.mach() as e:
                    e.run(chains, boundingBox, MACHINE_FEED, TABLE_UNITS, MACHINE_UNITS)
            except Exception as e:
                logging.warning("Tried %s but failed with %s" % (sand, e))
        logging.info("Job triggerd.")
        pprint(data)

    #for job in scheduler.get_jobs():
    #    print(job)
    #    job.remove()
        
    # add_job(func, trigger=None, args=None, kwargs=None, id=None, name=None, misfire_grace_time=undefined, coalesce=undefined, max_instances=undefined, next_run_time=undefined, jobstore='default',
    # executor='default', replace_existing=False, **trigger_args)
    
    #p = {
    #  "job":"testj"
    #}
    #job = scheduler.add_job(handleJob, 'cron', args=[p], second="*/15")
        
    #print("Current Jobs:")
    #for job in scheduler.get_jobs():
    #    print(job)

    # Start the socket server and listen for requests
    # Retry logic has been implemented because sometimes sockets don't release quickly
    logging.info("Trying to listen on %s:%d" % (SCHEDULER_HOST, SCHEDULER_PORT))
    retries = 10
    server = None
    while retries > 0:
        try:
            server = StoppableTCPServer((SCHEDULER_HOST, SCHEDULER_PORT), SchedulerSocketHandler)
            logging.info("SocketServer connected")
            break
        except socket.error as e:
            logging.error("%d retries left: %s" % (retries, e))
            retries -= 1
            time.sleep(10.0)
    if server:
        server.cb=handleJob
        server.jobHandler = jobHandler
        server.scheduler = scheduler
        server.serve()
    logging.info("Out of server loop!")

    scheduler.shutdown()
    jobHandler.stop()

    exit(1)
