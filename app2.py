#-*- coding: utf-8 -*-

from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template, _app_ctx_stack
from flaskext import *

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

import redis

"""
HOST = 'localhost'
DATABASE = 'nozomi'
DEBUG = True
PASSWORD = '2e4n5k2w2x'
"""


reload(sys)
sys.setdefaultencoding('utf-8') 

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

redisPool = redis.ConnectionPool(host="127.0.0.1")

def getServer():
    return redis.StrictRedis(connection_pool=redisPool)

sqls = ["SELECT u.id,%s,0,u.name,u.level,u.totalCrystal,c.icon,c.name FROM nozomi_user AS u LEFT JOIN `nozomi_clan` AS c ON u.clan=c.id WHERE u.id=%s", "SELECT u.id,%s,0,u.name,u.level,u.totalCrystal,u.uglevel,c.icon,c.name FROM nozomi_user AS u LEFT JOIN `nozomi_clan` AS c ON u.clan=c.id WHERE u.id=%s"]
@app.route('/v2/rank', methods=['GET'])
def getRank():
    rankMode = str(request.args['mode'])
    ruid = int(request.args['uid'])
    num = 100
    if ruid>0 and num>0:
        rserver = getServer()
        con = getConn()
        cur = con.cursor()
        allUsers = []
        uids = rserver.zrevrange(rankMode, 0, num-1, True)
        sql = sqls[0]
        if 'withug' in request.args:
            sql = sqls[1]
        if uids!=None:
            for uid in uids:
                cur.execute(sql,(int(uid[1]), int(uid[0])))
                allUsers.append(cur.fetchone())
        srank = rserver.zrevrank(rankMode, ruid)
        if srank==None or srank<num or len(allUsers)<num:
            cur.close()
            return json.dumps(allUsers)
        uids = rserver.zrevrange(rankMode, srank-1, srank+9, True)
        for i in range(len(uids)):
            if i+srank>num:
                cur.execute(sql,(int(uids[i][1]), int(uids[i][0])))
                item = cur.fetchone()
                if item==None:
                    rserver.zrem(rankMode, uids[i][0])
                    srank -= 1
                else:
                    item = list(item)
                    item.append(i+srank)
                    allUsers.append(item)
        cur.close()
        return json.dumps(allUsers)
    return "[]"

app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=9966)
