from bottle import route, get, template
from cgi import escape
from Sand import drawers, TABLE_WIDTH, TABLE_LENGTH, BALL_SIZE, TABLE_UNITS
from sandable import sandableFactory

overview = escape("""
Cron expressions.

Examples:
          every 5 minutes: */5 * * * * 
  every 00:00 on Saturday: 0 0 * * SAT  
      every day at 8:00am: 0 8 * * *
     every day at 11.30pm: 30 23 * * * 
     
minute   hour   day    month   day
              (month)         (week)

minute:
   *        any valye
   ,        value list seperator
   -        range of values
   /        step values
   0..59    values
   
hour:
   *        any valye
   ,        value list seperator
   -        range of values
   /        step values
   0..23    values
   
day(month):
   *        any valye
   ,        value list seperator
   -        range of values
   /        step values
   1..31    values
   
month:
   *        any valye
   ,        value list seperator
   -        range of values
   /        step values
   1..12    values
   JAN..DEC alternatve values
   
day(week):
   *        any valye
   ,        value list seperator
   -        range of values
   /        step values
   0..6     values
   SUN..SAT alternatve values
   7        sunday (non standard)

""", quote=True)


@route('/cronhelp')
@get('/cronhelp')
def helpPage():
    return [template('help-page', overview=overview, sandables=[], sandableFactory=sandableFactory,tableWidth=TABLE_WIDTH, tableLength=TABLE_LENGTH, ballSize=BALL_SIZE, tableUnits=TABLE_UNITS)]

