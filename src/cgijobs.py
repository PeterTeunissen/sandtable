from bottle import request, route, get, post, template

from dialog import Dialog, Params
from cgistuff import cgistuff
import schedapi
from pprint import pprint
from jobable import jobFactory
import logging
from Sand import GCODE_PATH, ledPatterns
from croniter import croniter

@route('/jobs')
@get('/jobs')
@post('/jobs')
def jobsPage():
    cstuff = cgistuff('Jobs', jQuery=True)
    form = request.forms

    err = ""

    if form.action=='delete' and form.deleteId:
        with schedapi.schedapi() as sched:
            d={}
            d['id']=form.deleteId
            sched.deleteJob(d)

    if form.action=='runNow' and form.jobId:
        with schedapi.schedapi() as sched:
            d={}
            d['id']=form.jobId
            sched.runJob(d)

    if form.action=='addlightjob':
        if croniter.is_valid(form.cron):
            with schedapi.schedapi() as sched:
                li = ledPatterns.index(form.modeStr)-1
                d={}
                d['jobtype']="lightjob"
                d['name']=form.name
                d['cron']=form.cron
                d['color']=form.color
                d['speed']=form.speed
                d['brightness']=form.brightness
                d['autoCycle']=form.autoCycle
                d['mode']= str(li)
                d['modeName']=form.modeStr
                sched.addJob(d)
        else:
            err = "cron expression not valid!"

    if form.action=='adddrawjob':
        if croniter.is_valid(form.cron):
            with schedapi.schedapi() as sched:
                d={}
                d['jobtype']="drawjob"
                d['name']=form.name
                d['cron']=form.cron
                d['filename']=form.filename
                d['randomize']=form.randomizeFile
                sched.addJob(d)
        else:
            err = "cron expression is not valid"

    with schedapi.schedapi() as sched:
        jobs = sched.getJobs()

    if form.formType=="lightjob":
        jobUI = jobFactory("Lights-Job-Params")
        jobType="lightjob"
    elif form.formType=="drawjob":
        jobUI = jobFactory("Draw-Job-Params")
        jobType="drawjob"
    else:
        jobUI = jobFactory("Draw-Job-Params")
        jobType="drawjob"

    pr = Params(jobUI.editor)

    #d['mode']= str(li)

    if form.brightness:
        pr['brightness']=form.brightness
    else:
        pr['brightness']=100

    if form.autoCycle:
        pr['autoCycle']=form.autoCycle
    else:
        pr['autoCycle']=False

    if form.speed:
        pr['speed']=form.speed
    else:
        pr['speed']=9000

#    if form.color:
#        pr['color']=form.color
#    else:
#        pr['color']=(255,0,0)

#    if form.randomizeFile:
#        pr['randomizeFile']=form.randomizeFile
#    else:
#        pr['randomizeFile']=False

#    if form.cron:
#        pr['cron']=form.cron
#    else:
#        pr['cron']=""

#    if form.name:
#        pr['name']=form.name
#    else:
#        pr['name']=""

#    if form.filename:
#        pr['filename']=form.filename
#    else:
#        pr['filename']=GCODE_PATH

    pr['errors']=[]

    d = Dialog(jobUI.editor, form, None, autoSubmit=False)
#    d = Dialog(jobUI.editor, form, pr, autoSubmit=False)
    params = d.getParams()

    #if form.method:
    #    with ledapi.ledapi() as led:
    #        led.setPattern(ledPattern, params)

    if jobs:
        pprint(jobs)
    else:
        print("No jobs found!")

    return [
        cstuff.standardTopStr(),
        template('jobs-page', jobs=jobs, editor=d.html(), jobType=jobType, errors=err),
        cstuff.endBodyStr()]
