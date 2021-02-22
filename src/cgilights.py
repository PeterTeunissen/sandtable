from bottle import request, route, get, post, template

from Sand import ledPatterns, LED_COLUMNS, LED_ROWS
from dialog import Dialog, Params
from cgistuff import cgistuff
from ledable import ledPatternFactory
import ledapi
import logging

@route('/lights')
@get('/lights')
@post('/lights')
def lightsPage():
    cstuff = cgistuff('Lights', jQuery=True)
    form = request.forms

    if form.method:
        #logging.info("From form speed: %s brightness: %s auto: %s" % (form.speed,form.brightness,form.autoCycle))
        with ledapi.ledapi() as led:
            if form.speed:
                led.setSpeed(form.speed)
            if form.brightness:
                led.setBrightness(form.brightness)
            if form.autoCycle:
                led.setAutoCycle(True if form.autoCycle=="True" else False)
            if form.color:
                led.setColor(form.color)
            if form.mode and form.mode!=-1:
                led.setMode(form.mode)

    with ledapi.ledapi() as led:        
        c_speed = led.getSpeed()
        c_mode = led.getMode()
        c_brightness = led.getBrightness()
        c_color = led.getColor()
        c_autocycle = led.getAutoCycle()
    
    ledPattern = form.method if form.method in ledPatterns else ledPatterns[0]
    pattern = ledPatternFactory(ledPattern, LED_COLUMNS, LED_ROWS)
    
    pr = Params(pattern.editor)
    pr['speed']=c_speed
    pr['color']=c_color
    pr['brightness']=c_brightness
    pr['autoCycle']=c_autocycle
    pr['errors']=""
    pr['mode']=c_mode
    
    d = Dialog(pattern.editor, form, pr, autoSubmit=True)
        
    params = d.getParams()

    with ledapi.ledapi() as led:
        if pattern.mode!=-1:
            led.setMode(pattern.mode)        

    with ledapi.ledapi() as led:
        c_speed = led.getSpeed()
        c_mode = led.getMode()
        c_brightness = led.getBrightness()
        c_color = led.getColor()
        c_autocycle = led.getAutoCycle()

    return [ cstuff.standardTopStr(),template('lights-page', pattern=ledPattern, ledPatterns=ledPatterns, editor=d.html(), c_speed=c_speed, c_color=c_color, c_brightness=c_brightness,c_autocycle=c_autocycle, c_mode=c_mode, sm=pattern.mode ), cstuff.endBodyStr()]

