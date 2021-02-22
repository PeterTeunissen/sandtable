from bottle import request, route, get, post, template

from dialog import Dialog, Params
from cgistuff import cgistuff
import schedapi
from pprint import pprint
from jobable import jobFactory
import logging
from Sand import MOVIE_SCRIPT_PATH

@route('/jobs')
@get('/jobs')
@post('/jobs')
def jobsPage():
    cstuff = cgistuff('Jobs', jQuery=True)
    form = request.forms

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
            
    if form.action=='add':
        with schedapi.schedapi() as sched:
            d={}
            d['name']=form.name
            d['cron']=form.cron
            d['filename']=form.filename
            d['params']=form.params
            d['job']=form.job
            sched.addJob(d)
        
    with schedapi.schedapi() as sched:
        jobs = sched.getJobs()

    jobUI = jobFactory("Job-Params")

    pr = Params(jobUI.editor)    

    if form.params:
        pr['params']=form.params
    else:
        pr['params']=""

    if form.job:
        pr['job']=form.job
    else:
        pr['job']=""
        
    if form.cron:
        pr['cron']=form.cron
    else:
        pr['cron']=""
        
    if form.name:
        pr['name']=form.name
    else:
        pr['name']=""
        
    if form.filename:
        pr['filename']=form.filename
    else:
        pr['filename']=MOVIE_SCRIPT_PATH
        
    pr['errors']=[]

    d = Dialog(jobUI.editor, form, pr, autoSubmit=False)
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
        template('jobs-page', jobs=jobs, editor=d.html()),
        cstuff.endBodyStr()]
