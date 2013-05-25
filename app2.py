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

reload(sys)
sys.setdefaultencoding('utf-8') 

app = Flask(__name__)

def getConn():
    return MySQLdb.connect(host='localhost', passwd='3508257', db='nozomi', user='root', charset='utf8')

@app.route("/updateScore")
def updateScore(): 
    myCon = getConn();
    uid = int(request.args['uid'])
    newScore = int(request.args['newScore'])
    UserRankModule.updateScore(myCon, uid, newScore)
    return json.dumps(dict(id=1))

@app.route('/getUserRank')
def getUserRank():
    myCon = getConn();
    uid = int(request.args['uid'])
    score = int(request.args['score'])
    rank = UserRankModule.getRank(myCon, score)
    l = UserRankModule.getRange(myCon, 0, 50)
    if len(l)<50 or rank<50:
        return json.dumps([[r['uid'], r['score'], r['lastRank'], r['name']] for r in l])
    else:
        zw = UserRankModule.getRange(myCon, rank-1, rank+9)
        inZw = False
        for z in zw:
            if z['uid']==uid:
                inZw = True
                break
        if not inZw:
            zw[1] = dict(uid=uid, lastRank=0, score=score)
        l = [[r['uid'], r['score'], r['lastRank'], r['name']] for r in l]
        for i in range(len(zw)):
            z = zw[i]
            if rank+i<=50:
                continue
            l.append([z['uid'],z['score'],z['lastRank'], z['name'],rank+i])
        return json.dumps(l)
    #return json.dumps(dict(rank=rank))

app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
