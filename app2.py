#-*- coding: utf-8 -*-

from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template
from flaskext import *
from module import *

import MySQLdb
import os, sys, time, datetime
import json
import logging
from calendar import monthrange
import config

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

def getConn():
    #return MySQLdb.connect(host='localhost', passwd='3508257', db='nozomi', user='root', charset='utf8')
    return MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')

def initUserRankModule():
    myCon = getConn()
    UserRankModule.initScoreCount(myCon)
    myCon.close()
initUserRankModule()



@app.route("/updateScore")
def updateScore(): 
    myCon = getConn();
    uid = int(request.args['uid'])
    newScore = int(request.args['score'])
    UserRankModule.updateScore(myCon, uid, newScore)
    return json.dumps(dict(id=1))


@app.route('/getUserRank')
def getUserRank():
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
    app.run(debug=True, host='0.0.0.0', port=9002)
