#-*- coding: utf-8 -*-

from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template, _app_ctx_stack
from flaskext import *
from module import *

import MySQLdb
import os, sys, time, datetime
import json
import logging
from calendar import monthrange
import config
import logging
from logging.handlers import TimedRotatingFileHandler
from logging import Formatter
import BufferMailHandler

from MySQLdb import cursors, connections

"""
HOST = 'localhost'
DATABASE = 'nozomi'
DEBUG = True
PASSWORD = '2e4n5k2w2x'
"""


reload(sys)
sys.setdefaultencoding('utf-8') 

#record mysql query time
mysqlLogHandler = TimedRotatingFileHandler('mysqlSortLog.log', 'd', 1)

mysqllogger = logging.getLogger("mysqlLogger")
mysqllogger.addHandler(mysqlLogHandler)
mysqllogger.setLevel(logging.INFO)

#oldExec = getattr(cursors.BaseCursor, 'execute')
oldQuery = getattr(connections.Connection, 'query')

"""
def execute(self, query, args=None):
    startTime = time.time()*1000
    oldExec(self, query, args)
    endTime = time.time()*1000
    mysqlLogHandler.info("%s %d", query, int(endTime-startTime))
"""
    
def query(self, sql):
    startTime = time.time()*1000
    oldQuery(self, sql)
    endTime = time.time()*1000
    mysqllogger.info("%s\t%d\t%s", sql, int(endTime-startTime), time.asctime())

#setattr(cursor.BaseCursor, 'execute', execute)
setattr(connections.Connection, 'query', query)



app = Flask(__name__)
app.config.from_object("config")


timeLogHandler = TimedRotatingFileHandler('nozomiRankAccess.log', 'd', 7)
timelogger = logging.getLogger("timeLogger")
timelogger.addHandler(timeLogHandler)
timelogger.setLevel(logging.INFO)

@app.before_request
def beforeQuest():
    g.startTime = time.time() 
    #print request.url
@app.after_request
def afterQuest(response):
    endTime = time.time()
    timelogger.info('%s %d  %d' % (request.url, int(g.startTime), int((endTime-g.startTime)*10**3)) )
    return response

debugLogger = logging.FileHandler("errorRank.log")
debugLogger.setLevel(logging.ERROR)
debugLogger.setFormatter(Formatter(
'''
Message type:  %(levelname)s
Module:        %(module)s
Time:          %(asctime)s
Message:
%(message)s
'''))
app.logger.addHandler(debugLogger)

mailLogger = BufferMailHandler.BufferMailHandler("127.0.0.1", "liyonghelpme@gmail.com", config.ADMINS, "Your Rank Application Failed!\ncheck errorRank.log file")
mailLogger.setLevel(logging.ERROR)
mailLogger.setFormatter(Formatter(
'''
Message type:  %(levelname)s
Location:      %(pathname)s:%(lineno)d
Module:        %(module)s
Function:      %(funcName)s
Time:          %(asctime)s
Message:
%(message)s
'''))
app.logger.addHandler(mailLogger)


@app.errorhandler(500)
def internalError(exception):
    print "internal error", request
    app.logger.exception('''
    args %s
    form %s
    %s
    ''' % (str(request.args), str(request.form), exception))
    return '', 500 


def getConn():
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')
    return top.db
@app.teardown_appcontext
def closeCon(excp):
    top = _app_ctx_stack.top
    if hasattr(top, 'db'):
        top.db.close()


def initUserRankModule():
    #myCon = getConn()
    #UserRankModule.initScoreCount(myCon)
    #myCon.close()
    pass
#initUserRankModule()



@app.route("/updateScore")
def updateScore(): 
    myCon = getConn();
    uid = int(request.args['uid'])
    newScore = int(request.args['score'])
    UserRankModule.updateScore(myCon, uid, newScore)
    return json.dumps(dict(id=1))

@app.route("/restoreScore")
def restoreScore():
    myCon = getConn()
    uid = int(request.args['uid'])
    newScore = int(request.args['score'])
    UserRankModule.updateScore(myCon, uid, newScore, force=True)
    return json.dumps(dict(id=1))


import cProfile, pstats, io
@app.route('/getUserRank')
def getUserRank():
    """
    pr = cProfile.Profile()
    pr.enable()
    """

    myCon = getConn();
    uid = int(request.args['uid'])
    score = int(request.args['score'])
    rank = UserRankModule.getRank(myCon, uid)
    l = UserRankModule.getRange(myCon, 0, 50)

    #user name 
    myCon.query('select name from nozomi_user where id = %d' % (uid))
    userInfo = myCon.store_result().fetch_row(0, 1)[0]

    if len(l)<50 or rank<50:
        return json.dumps([[r['uid'], r['score'], r['lastRank'], r['name'], r['icon'], r['cname']] for r in l])
    else:
        zw = UserRankModule.getRange(myCon, rank-1, rank+9)
        inZw = False
        for z in zw:
            if z['uid']==uid:
                inZw = True
                break
        #self not in ranking put me at first place
        if not inZw:
            zw[1] = dict(uid=uid, lastRank=0, score=score, name=userInfo['name'])
        l = [[r['uid'], r['score'], r['lastRank'], r['name'], r.get('icon'), r.get('cname')] for r in l]
        for i in range(len(zw)):
            z = zw[i]
            if rank+i<=50:
                continue
            l.append([z['uid'],z['score'],z['lastRank'], z['name'], z.get('icon'), z.get('cname'),rank+i])
        return json.dumps(l)
    #return json.dumps(dict(rank=rank))

app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.SORTPORT)
