#-*- coding: utf-8 -*-

from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template
#from datetime import datetime
#from flask import Flask, request, flash, url_for, redirect, \
#     render_template, abort
from flaskext import *
from module import *

import MySQLdb
import os, sys, time, datetime
import json
from calendar import monthrange

HOST = 'localhost'
DATABASE = 'nozomi'
DEBUG = True
PASSWORD = '2e4n5k2w2x'


reload(sys)
sys.setdefaultencoding('utf-8') 

app = Flask(__name__)
app.config.from_object(__name__)

dailyModule = DailyModule("nozomi_user_login")
achieveModule = AchieveModule("nozomi_achievement")

@app.errorhandler(501)
def user_not_login(error):
    return redirect(url_for('login'))

dataBuilds = [{'buildIndex':1, 'grid':190020, 'bid':1, 'level':1, 'time':0, 'hitpoints':0, 'extend':{'oil':1000, 'food':1000}},
              {'buildIndex':2, 'grid':130027, 'bid':1000, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':3, 'grid':210016, 'bid':2002, 'level':1, 'time':0, 'hitpoints':0, 'extend':{'resource': 500}},
              {'buildIndex':4, 'grid':250026, 'bid':2004, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':5, 'grid':260021, 'bid':2005, 'level':1, 'time':0, 'hitpoints':0, 'extend':{'resource':12}},
              {'buildIndex':6, 'grid':380002, 'bid':4007, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':7, 'grid':370013, 'bid':4004, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':8, 'grid':350027, 'bid':4012, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':9, 'grid':350035, 'bid':4014, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':10, 'grid':20006, 'bid':4013, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':11, 'grid':20021, 'bid':4009, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':12, 'grid':40036, 'bid':4014, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':13, 'grid':100002, 'bid':4008, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':14, 'grid':90014, 'bid':4006, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':15, 'grid':130017, 'bid':4002, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':16, 'grid':140021, 'bid':4014, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':17, 'grid':180017, 'bid':4012, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':18, 'grid':210004, 'bid':4009, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':19, 'grid':250009, 'bid':4000, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':20, 'grid':200030, 'bid':4004, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':21, 'grid':230030, 'bid':4009, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':22, 'grid':210038, 'bid':4008, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':23, 'grid':380010, 'bid':4003, 'level':1, 'time':0, 'hitpoints':0},
              {'buildIndex':24, 'grid':200027, 'bid':3000, 'level':1, 'time':0, 'hitpoints':0}
              ]

def getUserInfos(uid):
    r = queryOne("SELECT name, score, clan, level FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2], ulevel=r[3])

def getUserAllInfos(uid):
    r = queryOne("SELECT name, score, clan, level, exp, guideValue, crystal, lastSynTime, shieldTime, zombieTime, obstacleTime, zombieDefends FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2], ulevel=r[3], exp=r[4], guide=r[5], crystal=r[6], lastSynTime=r[7], shieldTime=r[8], zombieTime=r[9], obstacleTime=r[10], zombieDefends=r[11])

def updateUserInfoById(params, uid):
    sql = "UPDATE nozomi_user SET "
    isFirst = True
    paramList = []
    for key, value in params.items():
        if isFirst:
            isFirst = False
        else:
            sql = sql+","
        sql = sql + key + "=%s"
        paramList.append(value)
    sql = sql + " WHERE id=%s"
    paramList.append(uid)
    update(sql, paramList)

def getJsonObj(string):
    if string=="":
        return None
    else:
        return json.loads(string)
    
def getUserBuilds(uid):
    builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM nozomi_build WHERE id=%s AND state=0", (uid))
    return [dict(buildIndex=r[0], grid=r[1], bid=r[2], level=r[3], time=r[4], hitpoints=r[5], extend=getJsonObj(r[6])) for r in builds]

def deleteUserBuilds(uid, buildIndexes):
    params = []
    for bindex in buildIndexes:
        params.append([uid, bindex])
    executemany("UPDATE nozomi_build SET state=1 WHERE id=%s AND buildIndex=%s", params)

def updateUserBuilds(uid, datas):
    params = []
    for data in datas:
        extend = ""
        if 'extend' in data:
            extend = json.dumps(data['extend'])
        params.append([uid, data['buildIndex'], data['grid'], data['bid'], data['level'], data['time'], data['hitpoints'], extend])
    executemany("INSERT INTO nozomi_build (id, buildIndex, grid, state, bid, level, `time`, hitpoints, extend) VALUES(%s,%s,%s,0,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE grid=VALUES(grid),state=0,bid=VALUES(bid),level=VALUES(level),`time`=VALUES(time),hitpoints=VALUES(hitpoints),extend=VALUES(extend);", params)

def getUidByName(account):
    ret = queryOne("SELECT id FROM nozomi_user WHERE account=%s", (account))
    if ret==None:
        return 0
    else:
        return ret[0]

def initUser(username, nickname):
    regTime = int(time.mktime(time.localtime()))
    uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, score, crystal, shieldTime) VALUES(%s, %s, %s, 500, 497, 0)", (username, regTime, nickname))
    updateUserBuilds(uid, dataBuilds)
    newUserState(uid)
    return uid

def updateUserState(uid, eid):
    updateUserOnline(uid)
    if eid!=0:
        clearUserAttack(eid)

def setUserClan(uid, cid):
    update("UPDATE nozomi_user SET clan=%s WHERE id=%s", (cid, uid))

def createClan(uid, name, ctype, minScore):
    cid = insertAndGetId("INSERT INTO nozomi_clan (name, type, minScore, creator, members, score) VALUES (%s, %s, %s, %s, 1, 0)", (name, ctype, minScore, uid))
    setUserClan(uid, cid)
    return cid

def addClanMember(cid, uid):
    setUserClan(uid, cid)
    update("UPDATE nozomi_clan SET members=members+1 WHERE id=%s", (cid))

def getClanInfo(cid):
    return queryOne("SELECT name, type, minScore, creator, members, score FROM nozomi_clan WHERE id=%s", (cid))

def getClanMembers(cid):
    ret = queryAll("SELECT id, name, score FROM nozomi_user WHERE clan=%s", (cid))
    return [dict(id=r[0], name=r[1], score=r[2]) for r in ret]

@app.route("/findClans", methods=['GET'])
def findClans():
    ret = queryAll("SELECT id, name, type, minScore, creator, members, score FROM nozomi_clan LIMIT 50")
    if ret==None:
        return "[]"
    return json.dumps([dict(id=r[0], name=r[1], type=r[2], minScore=r[3], members=r[5], score=r[6]) for r in ret])

@app.route("/getClanInfos", methods=['GET'])
def getClanInfos():
    cid = int(request.args['cid'])
    clanInfo = getClanInfo(cid)
    ret = dict(id=cid, name=clanInfo[0], type=clanInfo[1], minScore=clanInfo[2], creator=clanInfo[3], members=clanInfo[4], score=clanInfo[5])
    ret['memberInfos'] = getClanMembers(cid)
    return json.dumps(ret)

@app.route("/createClan", methods=['POST'])
def createSelfClan():
    if 'uid' not in request.form:
        return json.dumps(dict(code=401, msg="user id require"))
    if 'name' not in request.form:
        return json.dumps(dict(code=401, msg="clan name require"))
    uid = int(request.form['uid'])
    name = request.form['name']
    cid = createClan(uid, name, 0, 0)
    return json.dumps(dict(code=0, cid=cid))

@app.route("/searchClan", methods=['GET'])
def searchClan():
    match = request.args['match']
    ret = queryAll("SELECT id, name, type, minScore, creator, members, score FROM nozomi_clan WHERE name LIKE %s", ("%"+match+"%"))
    if ret==None:
        return "[]"
    return json.dumps([dict(id=r[0], name=r[1], type=r[2], minScore=r[3], members=r[5], score=r[6]) for r in ret])

@app.route("/joinClan", methods=['POST'])
def joinClan():
    if 'cid' not in request.form:
        return json.dumps(dict(code=401, msg="clan id require"))
    if 'uid' not in request.form:
        return json.dumps(dict(code=401, msg="user id require"))
    cid = int(request.form['cid'])
    uid = int(request.form['uid'])
    clanInfo = getClanInfo(cid)
    if clanInfo==None or clanInfo[1]==2:
        return json.dumps(dict(code=1, msg="This clan is closed"))
    elif clanInfo[4]==50:
        return json.dumps(dict(code=2, msg="Clan is full"))
    userInfo = getUserInfos(uid)
    if userInfo==None:
        return json.dumps(dict(code=3, msg="User not exsited"))
    elif userInfo[2]<clanInfo[2]:
        return json.dumps(dict(code=4, msg="Score is limited"))
    if userInfo[5]==0:
        if clanInfo[1]==1:
            #add msg to clan
            return json.dumps(dict(code=0, type=1, cid=cid))
        else:
            addClanMember(cid, uid)
            #add msg to clan
            return json.dumps(dict(code=0, type=0, cid=cid))
    else:
        return json.dumps(dict(code=2, msg="User was already in a clan"))

@app.route("/login", methods=['POST'])
def login():
    if 'username' in request.form:
        username = request.form['username']
        uid = getUidByName(username)
        ret = dict(code=0, uid=uid)
        if uid==0:
            nickname = request.form['nickname']
            uid = initUser(username, nickname)
            achieveModule.initAchieves(uid)
            ret['uid'] = uid
        else:
            days = dailyModule.dailyLogin(uid)
            if days>0:
                ret['days']=days

        con = MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')
        sql = 'select * from nozomi_params'
        con.query(sql)
        res = con.store_result().fetch_row(0, 1)
        params = dict()
        for r in res:
            params[r['key']] = int(r['value'])
        """
        sql = 'select * from nozomi_zombie_attack'
        con.query(sql)
        res = con.store_result().fetch_row(0, 1)
        waves = []
        for i in range(9):
            waves.append([])
            for j in range(3):
                waves[i].append([])
                for k in range(8):
                    waves[i][j].append(0)
        for r in res:
            item = waves[int(r['nozomi_level'])-1][int(r['attack_wave'])-1]
            for i in range(8):
                item[i] = int(r['zombie%d_num' % (i+11)])
        params['attackWaves'] = waves
        """
        ret['params'] = params
        con.close()
        return json.dumps(ret)
    else:
        return "{'code':401}"

@app.route("/getData", methods=['GET'])
def getData():
    uid = int(request.args.get("uid"))
    infos = None
    if True: #"login" in request.args:
        state = getUserState(uid)
        if 'attackTime' in state:
            return json.dumps(state)
        data = getUserAllInfos(uid)
        data['serverTime'] = int(time.mktime(time.localtime()))
        if data['lastSynTime']==0:
            data['lastSynTime'] = data['serverTime']
        data['achieves'] = achieveModule.getAchieves(uid)
    else:
        infos = getUserInfos(uid)
    data['builds'] = getUserBuilds(uid)
    return json.dumps(data)

@app.route("/synData", methods=['POST'])
def synData():
    uid = int(request.form.get("uid", 0))
    if uid==0:
        return json.dumps({'code':401})
    if 'delete' in request.form:
        delete = json.loads(request.form['delete'])
        deleteUserBuilds(uid, delete)
    if 'update' in request.form:
        #print("test_update", request.form['update'])
        update = json.loads(request.form['update'])
        updateUserBuilds(uid, update)
    if 'achieves' in request.form:
        #print("receive achieves", request.form['achieves'])
        achieves = json.loads(request.form['achieves'])
        achieveModule.updateAchieves(uid, achieves)
    userInfoUpdate = dict(lastSynTime=int(time.mktime(time.localtime())))
    #if 'shieldTime' in request.form:
    #    userInfoUpdate['shieldTime'] = int(request.form['shieldTime'])
    #if 'guide' in request.form:
    #    userInfoUpdate['guideValue'] = int(request.form['guide'])
    if 'userInfo' in request.form:
        userInfo = json.loads(request.form['userInfo'])
        userInfoUpdate.update(userInfo)
        if 'shieldTime' in userInfo:
            setUserShield(uid, userInfo['shieldTime'])
    updateUserInfoById(userInfoUpdate, uid)
    updateUserState(uid, int(request.form.get("eid", 0)))
    return json.dumps({'code':0})

@app.route("/synBattleData", methods=['POST'])
def synBattleData():
    uid = int(request.form.get("uid", 0))
    eid = int(request.form.get("eid", 0))
    if uid==0 or eid==0:
        return json.dumps({'code':401})
    if 'delete' in request.form:
        delete = json.loads(request.form['delete'])
        deleteUserBuilds(eid, delete)
    if 'update' in request.form:
        #print("test_update", request.form['update'])
        update = json.loads(request.form['update'])
        updateUserBuilds(eid, update)
    incScore = int(request.form.get("score", 0))
    baseScore = getUserInfos(eid)['score']
    userInfoUpdate=dict(score=baseScore+incScore)
    if 'shieldTime' in request.form:
        t = int(request.form['shieldTime'])
        userInfoUpdate['shieldTime'] = t
        setUserShield(eid, t)
    updateUserInfoById(userInfoUpdate, eid)
    #if 'guide' in request.form:
    #    userInfoUpdate['guideValue'] = int(request.form['guide'])
    updateUserState(uid, eid)
    return json.dumps({'code':0})

@app.route("/findEnemy", methods=['GET'])
def findEnemy():
    selfUid = int(request.args.get('uid', 0))
    updateUserState(selfUid, int(request.args.get("eid", 0)))
    isGuide = request.args.get('isGuide')
    uid = 10
    if isGuide==None:
        uid = findAMatch(selfUid, int(request.args.get('baseScore', 0)), 1000)
    #uid = 8
    data = getUserInfos(uid)
    data['builds'] = getUserBuilds(uid)
    data['userId'] = uid
    return json.dumps(data)

@app.route("/sendFeedback", methods=['POST'])
def sendFeedback():
    uid = int(request.form.get('uid', 0))
    if uid!=0:
        text=request.form.get('text')
        if text!=None:
            update("INSERT INTO nozomi_feedback (uid, text) VALUES (%s,%s)", (uid, text))
            return json.dumps(dict(code=0))
    return json.dumps(dict(code=401))
    
app.secret_key = os.urandom(24)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = 9000)
