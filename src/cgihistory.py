from bottle import route, template
from os import stat
from Sand import STORE_PATH
from cgistuff import cgistuff
from history import History
import datetime

@route('/history')
def historyPage():
    cstuff = cgistuff('Drawing History')

    def ftime(x): return [datetime.datetime.fromtimestamp(stat('%s%s.png' % (STORE_PATH, name)).st_mtime).strftime("%m/%d/%Y %H:%M:%S") for name in x]
    def mtimes(x): return [stat('%s%s.png' % (STORE_PATH, name)).st_mtime for name in x]
    save, history, jobs = History.list()

    return [
        cstuff.standardTopStr(),
        template('history-page', save=save, history=history, path=STORE_PATH, mtimes=mtimes, jobs=jobs, ftime=ftime),
        cstuff.endBodyStr()]
