#-*- coding: utf-8 -*-

from flask import Flask, g, abort, session, redirect, url_for, \
     request, render_template, _app_ctx_stack, jsonify
#from datetime import datetime
#from flask import Flask, request, flash, url_for, redirect, \
#     render_template, abort
from flaskext import *
from module import *

import MySQLdb
import os, sys, time, datetime
import json, urllib2
import logging
from calendar import monthrange
import config
import module

#from requestlogger import WSGILogger, ApacheFormatter
from logging.handlers import TimedRotatingFileHandler
import time

from logging import Formatter
import BufferMailHandler
import util

from MySQLdb import cursors, connections
from werkzeug.contrib.fixers import ProxyFix



mysqlLogHandler = TimedRotatingFileHandler('mysqlLog.log', 'd', 1)

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



reload(sys)
sys.setdefaultencoding('utf-8') 

#配置文件里面不能有注释 
#不能有其它import 之类的声明
#只能有 键值对
app = Flask(__name__)
app.config.from_object("config")

timeLogHandler = TimedRotatingFileHandler('/data/allLog/nozomiAccess_2.log', 'd', 7)
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


@app.errorhandler(500)
def internalError(exception):
    print "internal error", request
    app.logger.exception('''
    args %s
    form %s
    %s
    ''' % (str(request.args), str(request.form), exception))
    return '', 500 
    
    
#可能没有web 上下文环境
def getConn():
    return MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')


def getMyConn():
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')
    return top.db

@app.teardown_appcontext
def closeCon(excp):
    top = _app_ctx_stack.top
    if hasattr(top, 'db'):
        top.db.close()

dailyModule = DailyModule("nozomi_user_login")
achieveModule = AchieveModule("nozomi_achievement")

statlogger = logging.getLogger("STAT")
#f = logging.FileHandler("stat.log")
f = TimedRotatingFileHandler('/data/allLog/stat_2.log', 'd', 1)
statlogger.addHandler(f)
formatter = logging.Formatter("%(asctime)s\t%(message)s")   
f.setFormatter(formatter)
statlogger.setLevel(logging.INFO)

loginlogger = logging.getLogger("LOGIN")
f = TimedRotatingFileHandler('/data/allLog/login_2.log','d',1)
loginlogger.addHandler(f)
formatter = logging.Formatter("%(asctime)s\t%(message)s")
f.setFormatter(formatter)
loginlogger.setLevel(logging.INFO)

crystallogger = logging.getLogger("CRYSTAL")
#f = logging.FileHandler("crystal_stat.log")
f = TimedRotatingFileHandler('/data/allLog/crystal_stat_2.log', 'd', 1)
crystallogger.addHandler(f)
formatter = logging.Formatter("%(asctime)s\t%(message)s")   
f.setFormatter(formatter)
crystallogger.setLevel(logging.INFO)


debugLogger = TimedRotatingFileHandler("/data/allLog/nozomiError_2.log", 'd', 7)
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

"""
mailLogger = BufferMailHandler.BufferMailHandler("127.0.0.1", "liyonghelpme@gmail.com", config.ADMINS, "Your Application Failed!\ncheck nozomiError.log file")
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
"""


#handlers = [TimedRotatingFileHandler('nozomiAccess.log', 'd', 7), ]



@app.errorhandler(501)
def user_not_login(error):
    return redirect(url_for('login'))

dataBuilds = [
              [1, 170018, 1, 1, 0, 1500, "{\"oil\":1000,\"food\":1000}"],
              [2, 110009, 2, 0, 0, 0, ""],
              [3, 130025, 2002, 1, 0, 400, "{\"resource\":500}"],
              [4, 250019, 2005, 1, 0, 400, "{\"resource\":100}"],
              [5, 240023, 2004, 1, 0, 250, "{\"resource\":1}"],
              [6, 180025, 1000, 1, 0, 400, ""],
              [7, 150030, 3000, 1, 0, 400, ""],
              [8, 180013, 1004, 1, 0, 400, ""],
              [9, 350003, 1003, 0, 0, 0, ""],
              [10, 40008, 4013, 1, 0, 0, ""],
              [11, 60005, 4007, 1, 0, 0, ""],
              [12, 90009, 4012, 1, 0, 0, ""],
              [13, 90011, 4006, 1, 0, 0, ""],
              [14, 110006, 4014, 1, 0, 0, ""],
              [15, 110012, 4009, 1, 0, 0, ""],
              [16, 140009, 4002, 1, 0, 0, ""],
              [17, 140011, 4004, 1, 0, 0, ""],
              [18, 170008, 4012, 1, 0, 0, ""],
              [19, 160004, 4007, 1, 0, 0, ""],
              [20, 30017, 4008, 1, 0, 0, ""],
              [21, 30024, 4000, 1, 0, 0, ""],
              [22, 20036, 4009, 1, 0, 0, ""],
              [23, 60029, 4001, 1, 0, 0, ""],
              [24, 100036, 4001, 1, 0, 0, ""],
              [25, 130033, 4003, 1, 0, 0, ""],
              [26, 180035, 4002, 1, 0, 0, ""],
              [27, 100021, 4007, 1, 0, 0, ""],
              [28, 250012, 4001, 1, 0, 0, ""],
              [29, 300017, 4014, 1, 0, 0, ""],
              [30, 300023, 4012, 1, 0, 0, ""],
              [31, 220003, 4004, 1, 0, 0, ""],
              [32, 270006, 4002, 1, 0, 0, ""],
              [33, 250030, 4009, 1, 0, 0, ""],
              [34, 250035, 4004, 1, 0, 0, ""],
              [35, 210038, 4008, 1, 0, 0, ""],
              [36, 350001, 4008, 1, 0, 0, ""],
              [37, 350007, 4008, 1, 0, 0, ""],
              [38, 370001, 4012, 1, 0, 0, ""],
              [39, 370007, 4013, 1, 0, 0, ""],
              [40, 330003, 4001, 1, 0, 0, ""],
              [41, 390003, 4000, 1, 0, 0, ""],
              [42, 330005, 4012, 1, 0, 0, ""],
              [43, 390005, 4012, 1, 0, 0, ""],
              [44, 370020, 4004, 1, 0, 0, ""],
              [45, 370024, 4012, 1, 0, 0, ""],
              [46, 340029, 4001, 1, 0, 0, ""],
              [47, 360033, 4003, 1, 0, 0, ""],
              [48, 330036, 4008, 1, 0, 0, ""],
              [49, 370037, 4014, 1, 0, 0, ""],
              [50, 20002, 4003, 1, 0, 0, ""]
              ]

def getUserInfos(uid):
    r = queryOne("SELECT name, score, clan, memberType FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2], mtype=r[3])

def getUserAllInfos(uid):
    r = queryOne("SELECT name, score, clan, guideValue, crystal, lastSynTime, shieldTime, zombieTime, obstacleTime, memberType, totalCrystal, lastOffTime FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2], guide=r[3], crystal=r[4], lastSynTime=r[5], shieldTime=r[6], zombieTime=r[7], obstacleTime=r[8], mtype=r[9], totalCrystal=r[10], lastOffTime=r[11])

def getBindGameCenter(tempName):
    r = queryOne("SELECT gameCenter FROM `nozomi_gc_bind` WHERE uuid=%s",(tempName))
    if r==None:
        return tempName
    else:
        return r

def bindGameCenter(gc,uuid):
    r = update("INSERT IGNORE INTO `nozomi_gc_bind` (gameCenter, uuid) VALUES (%s,%s)", (gc,uuid))
    if r==1:
        update("UPDATE IGNORE `nozomi_user` SET account=%s WHERE account=%s",(gc,uuid))

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
    builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM nozomi_build WHERE id=%s AND state=0", (uid), util.getDBID(uid))
    return builds

def deleteUserBuilds(uid, buildIndexes):
    params = []
    for bindex in buildIndexes:
        params.append([uid, bindex])
    executemany("UPDATE nozomi_build SET state=1 WHERE id=%s AND buildIndex=%s", params, dbID=util.getDBID(uid))

def updateUserBuilds(uid, datas):
    params = []
    for data in datas:
        params.append([uid, data[0], data[1], data[2], data[3], data[4], data[5], data[6]])
    executemany("INSERT INTO nozomi_build (id, buildIndex, grid, state, bid, level, `time`, hitpoints, extend) VALUES(%s,%s,%s,0,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE grid=VALUES(grid),state=0,bid=VALUES(bid),level=VALUES(level),`time`=VALUES(time),hitpoints=VALUES(hitpoints),extend=VALUES(extend);", params, util.getDBID(uid))

def getUserResearch(uid):
    researches = queryOne("SELECT research FROM nozomi_research WHERE id=%s", (uid))
    return json.loads(researches[0])

def updateUserResearch(uid, researches):
    update("UPDATE nozomi_research SET research=%s WHERE id=%s", (json.dumps(researches), uid))
    
def updateUserBuildHitpoints(uid, datas):
    params = []
    for data in datas:
        params.append([data[1], uid, data[0]])
    executemany("UPDATE nozomi_build SET hitpoints=%s WHERE id=%s AND buildIndex=%s", params, util.getDBID(uid))

def updateUserBuildExtends(uid, datas):
    params = []
    for data in datas:
        params.append([data[1], uid, data[0]])
    executemany("UPDATE nozomi_build SET extend=%s WHERE id=%s AND buildIndex=%s", params, util.getDBID(uid))

def getUidByName(account):
    ret = queryOne("SELECT id FROM nozomi_user WHERE account=%s", (account))
    if ret==None:
        return 0
    else:
        return ret[0]

def updateCrystal(uid, crystal):
    update("UPDATE `nozomi_user` SET crystal=crystal+%s WHERE id=%s", (crystal, id))

def updatePurchaseCrystal(uid, crystal, ctype):
    if ctype>4:
        update("UPDATE `nozomi_user` SET totalCrystal=totalCrystal+%s, lastOffTime=%s WHERE id=%s", (crystal, time.mktime(time.localtime()), uid))
    else:
        update("UPDATE `nozomi_user` SET totalCrystal=totalCrystal+%s WHERE id=%s", (crystal, uid))

def initUser(username, nickname, platform):
    print "initUser", username, nickname
    regTime = int(time.mktime(time.localtime()))
    platformId = 0
    if platform=="android":
        platformId=1
    initScore = 500
    uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, registerTime, score, crystal, shieldTime, platform) VALUES(%s, %s, %s, %s, 500, 497, 0, %s)", (username, regTime, nickname, util.getTime(), platformId))
    myCon = getConn()
    module.UserRankModule.initUserScore(myCon, uid, initScore)
    module.UserRankModule.updateScore(myCon, uid, initScore)
    myCon.commit()
    myCon.close()

    updateUserBuilds(uid, dataBuilds)
    update("INSERT INTO nozomi_research (id, research) VALUES(%s, '[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]')", (uid))
    newUserState(uid)
    
    return uid

def updateUserState(uid, eid):
    updateUserOnline(uid)
    if eid!=0:
        clearUserAttack(eid)

@app.route("/getBattleHistory", methods=['GET'])
def getBattleHistory():
    uid = int(request.args['uid'])
    ret = queryAll("SELECT info, eid, time, videoId, reverged FROM nozomi_battle_history WHERE uid=%s" , (uid))
    if ret==None:
        return "[]"
    else:
        return json.dumps([[json.loads(r[0]), r[1], r[2], r[3], r[4]] for r in ret])

@app.route("/login", methods=['POST', 'GET'])
def login():
    print 'login', request.form
    tempname = None
    if 'tempname' in request.form:
        tempname = request.form['username']
    username = None
    if 'username' in request.form:
        username = request.form['username']
    if tempname!=None:
        if username==None:
            username = getBindGameCenter(tempname)
        else:
            bindGameCenter(username, tempname)
    if username!=None:
        uid = getUidByName(username)
        ret = dict(code=0, uid=uid)
        if uid==0:
            print "new user"
            nickname = request.form['nickname']
            platform = "ios"
            if 'platform' in request.form:
                platform = request.form['platform']
            uid = initUser(username, nickname, platform)
            loginlogger.info("%s\t%d\treg" % (platform,uid))
            achieveModule.initAchieves(uid)
            ret['uid'] = uid
        #elif user[1]>=1400:
        #    days = dailyModule.dailyLogin(uid)
        #    if days>0:
        #        ret['days']=days
        #        reward = int((50+30*days)**0.5+0.5)
        #        updateCrystal(uid, reward)
        #        ret['reward'] = reward

        if False:

            con = MySQLdb.connect(host="192.168.3.105", user='root', passwd="badperson", db="nozomi", charset='utf8')
            sql = 'select * from nozomi_params'
            con.query(sql)
            res = con.store_result().fetch_row(0, 1)
            params = dict()
            for r in res:
                params[r['key']] = int(r['value'])
            sql = 'select * from nozomi_zombie_attack'
            con.query(sql)
            res = con.store_result().fetch_row(0, 1)
            waves = []
            for i in range(9):
                waves.append([])
                for j in range(1):
                    waves[i].append([])
                    for k in range(8):
                        waves[i][j].append(0)
            for r in res:
                item = waves[int(r['nozomi_level'])-1][int(r['attack_wave'])-1]
                for i in range(8):
                    item[i] = int(r['zombie%d_num' % (i+11)])
            params['attackWaves'] = waves
            ret['params'] = params
            con.close()

        return json.dumps(ret)
    else:
        #time.sleep(209) 
        return "{'code':401}"
        #测试timeout
        #pass

@app.route("/getData", methods=['GET'])
def getData():
    print 'getData', request.args
    uid = int(request.args.get("uid"))
    data = None
    if "login" in request.args:
        state = getUserState(uid)
        if 'attackTime' in state:
            return json.dumps(state)
        data = getUserAllInfos(uid)
        data['serverTime'] = int(time.mktime(time.localtime()))
        if data['lastSynTime']==0:
            data['lastSynTime'] = data['serverTime']
        platform = "ios"
        if 'platform' in request.form:
            platform = request.args['platform']
        data['achieves'] = achieveModule.getAchieves(uid)
        if data['guide']>=1400:
            days = dailyModule.dailyLogin(uid)
            if days>0:
                data['days']=days
                reward = int((50+30*days)**0.5+0.5)
                if days!=7 and days!=14 and days!=30:
                    updateCrystal(uid, reward)
                    data['crystal'] = data['crystal']+reward
                data['reward'] = reward
        loginlogger.info("%s\t%d\tlogin" % (platform,uid))
    else:
        data = getUserInfos(uid)
    if data['clan']>0:
        data['clanInfo'] = ClanModule.getClanInfo(data['clan'])
    data['builds'] = getUserBuilds(uid)
    data['researches'] = getUserResearch(uid)
    return json.dumps(data)

@app.route("/reverge", methods=['GET'])
def revergeGetData():
    uid = int(request.args.get("uid"))
    eid = int(request.args.get("eid"))
    state = getUserState(eid)
    if 'attackTime' in state:
        return json.dumps(dict(code=1))
    elif 'onlineTime' in state:
        return json.dumps(dict(code=2))
    elif 'shieldTime' in state:
        return json.dumps(dict(code=3))
    else:
        data = getUserInfos(eid)
        data['builds'] = getUserBuilds(eid)
        data['code'] = 0
        return json.dumps(data)

@app.route("/getReplay", methods=['GET'])
def getReplay():
    vid = int(request.args.get("vid"))
    return queryOne("SELECT replay FROM nozomi_replay WHERE id=%s", (vid))[0]

@app.route("/verify", methods=['POST'])
def verifyIAP():
    receipt = request.form.get("receipt")
    if receipt!=None:
        postData = json.dumps({'receipt-data':receipt})
        url = "https://buy.itunes.apple.com/verifyReceipt"
        #url = "https://sandbox.itunes.apple.com/verifyReceipt"
        req = urllib2.Request(url,postData)
        rep = urllib2.urlopen(req)
        page = rep.read()
        #update("INSERT INTO `buyCrystalVerify` (verify_code,verify_result) VALUES(%s,%s)", (receipt,page))
        result = json.loads(page)
        if result['status']==0:
            receipt = result['receipt']
            if int(receipt['original_purchase_date_ms'][:-3])>int(time.mktime(time.localtime())-86400):
                uniqInsert = update("INSERT IGNORE INTO `nozomi_iap_record` (transaction_id, buy_item, verify_data) VALUES(%s,%s,%s)",(receipt['original_transaction_id'],receipt['product_id'],page))
                if uniqInsert>0:
                    return "success"
    return "fail"

@app.route("/synData", methods=['POST'])
def synData():
    #print 'synData', request.form
    uid = int(request.form.get("uid", 0))
    if uid==0:
        return json.dumps({'code':401})
    platform = "ios"
    if 'platform' in request.form:
        platform = request.form['platform']
    if 'days' in request.form:
        days = int(request.form['days'])
        dailyModule.loginWithDays(uid, days)
    if 'delete' in request.form:
        delete = json.loads(request.form['delete'])
        deleteUserBuilds(uid, delete)
    if 'update' in request.form:
        update = json.loads(request.form['update'])
        updateUserBuilds(uid, update)
    if 'achieves' in request.form:
        achieves = json.loads(request.form['achieves'])
        achieveModule.updateAchieves(uid, achieves)
    if 'research' in request.form:
        researches = json.loads(request.form['research'])
        updateUserResearch(uid, researches)
    #先得到 现有的数据
    #更新的数据
    #话费的数据

    #连接结束自动关闭
    #myCon = getMyConn()
    #sql = 'select crystal from nozomi_user where id = %d' % (uid)
    #myCon.query(sql)

    #res = myCon.store_result().fetch_row(0, 1)
    #oldCrystal = res[0]['crystal']
    #newCrystal = None

    userInfoUpdate = dict(lastSynTime=int(time.mktime(time.localtime())))
    if 'userInfo' in request.form:
        userInfo = json.loads(request.form['userInfo'])
        userInfoUpdate.update(userInfo)
        if 'shieldTime' in userInfo:
            setUserShield(uid, userInfo['shieldTime'])
        #获得当前的新水晶数量
        #newCrystal = userInfoUpdate.get('crystal', None)


    updateUserInfoById(userInfoUpdate, uid)
    updateUserState(uid, int(request.form.get("eid", 0)))
    if 'stat' in request.form:
        statlogger.info("%s\t%d\t%s" % (platform, uid, request.form['stat']))
    if 'crystal' in request.form:
        ls = json.loads(request.form['crystal'])
        for l in ls:
            crystallogger.info("%s\t%d\t%s" % (platform, uid, json.dumps(l)))
            if l[0] == -1:
                updatePurchaseCrystal(uid, l[2], l[3])

    loginlogger.info("%s\t%d\tsynData" % (platform,uid))
    return json.dumps({'code':0})

@app.route("/synBattleData", methods=['POST'])
def synBattleData():
    #print 'synBattleData', request.form
    uid = int(request.form.get("uid", 0))
    eid = int(request.form.get("eid", 0))
    print("test uid and eid %d,%d" % (uid, eid))
    if uid==0 or eid==0:
        return json.dumps({'code':401})
    incScore = int(request.form.get("score", 0))
    if eid>1 and 'isLeague' not in request.form:
        if 'delete' in request.form:
            delete = json.loads(request.form['delete'])
            deleteUserBuilds(eid, delete)
        if 'eupdate' in request.form:
            #print("test_update", request.form['update'])
            up = json.loads(request.form['eupdate'])
            updateUserBuildExtends(eid, up)
        if 'hits' in request.form:
            hits = json.loads(request.form['hits'])
            updateUserBuildHitpoints(eid, hits)
        baseScore = getUserInfos(eid)['score']
        userInfoUpdate=dict(score=baseScore+incScore)
        if 'shieldTime' in request.form:
            t = int(request.form['shieldTime'])
            userInfoUpdate['shieldTime'] = t
            setUserShield(eid, t)
        updateUserInfoById(userInfoUpdate, eid)
    updateUserState(uid, eid)
    reverged = 0
    if 'isReverge' in request.form:
        reverged = 1
        update("UPDATE nozomi_battle_history SET reverged=1 WHERE uid=%s AND eid=%s", (uid, eid))
    if eid>1:
        videoId = 0
        if 'replay' in request.form:
            videoId = insertAndGetId("INSERT INTO nozomi_replay (replay) VALUES(%s)", (request.form['replay']))
        if 'isLeague' in request.form:
            lscore = int(request.form.get('lscore', 0))
            bid = int(request.form.get('bid', 0))
            cid = int(request.form.get('cid', 0))
            ecid = int(request.form.get('ecid', 0))
            ClanModule.changeBattleState(uid, eid, cid, ecid, bid, videoId, lscore)
        if 'history' in request.form:
            update("INSERT INTO nozomi_battle_history (uid, eid, videoId, `time`, `info`, reverged) VALUES(%s,%s,%s,%s,%s,%s)", (eid, uid, videoId, int(time.mktime(time.localtime())), request.form['history'], reverged))
    return json.dumps({'code':0})

@app.route("/findEnemy", methods=['GET'])
def findEnemy():
    selfUid = int(request.args.get('uid', 0))
    print("selfUid", selfUid)
    isGuide = request.args.get('isGuide')
    uid = 1
    #uid = 37
    if isGuide==None:
        uid = findAMatch(selfUid, int(request.args.get('baseScore', 0)), 200)
    #uid = 29
    print("Find Enemy:%d" % uid)

    if uid != 0:
        data = getUserInfos(uid)
        data['builds'] = getUserBuilds(uid)
        data['userId'] = uid
        updateUserState(selfUid, int(request.args.get("eid", 0)))
    else: #cant find a enemy
        data = {'code':1}
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

@app.route("/getClanMembers", methods=['GET'])
def getClanMembers():
    cid = int(request.args.get('cid', 0))
    if cid==0:
        return "[]"
    return json.dumps(ClanModule.getClanMembers(cid))

@app.route("/getRandomClans", methods=['GET'])
def getRandomClans():
    score = int(request.args.get('score', 0))
    return json.dumps(ClanModule.getRandomClans(score))

@app.route("/searchClans", methods=['GET'])
def searchClans():
    text = request.args.get('word')
    if text==None:
        return "null"
    return json.dumps(ClanModule.searchClans(text))

@app.route("/findLeagueEnemy", methods=['POST'])
def findLeagueEnemy():
    uid = int(request.form.get('uid', 0))
    cid = int(request.form.get('cid', 0))
    score = int(request.form.get('score', 0))
    if not ClanModule.checkFindLeagueAuth(uid, cid):
        return json.dumps(dict(code=2))
    clan = ClanModule.getClanInfo(cid)
    if clan[9]!=0:
        return json.dumps(dict(code=3,state=clan[9],statetime=clan[10]))
    enemy=ClanModule.findLeagueEnemy(cid, score)
    if 'eid' in request.form:
        eid = int(request.form.get('eid', 0))
        ClanModule.resetClanState(eid, 1)
    return json.dumps(dict(code=0, enemy=enemy))

@app.route("/cancelFindLeagueEnemy", methods=['POST'])
def cancelFindLeagueEnemy():
    cid = int(request.form.get('cid', 0))
    uid = int(request.form.get('uid', 0))
    
    if not ClanModule.checkFindLeagueAuth(uid, cid):
        return json.dumps(dict(code=2))
    ret = 1
    if cid>0:
        clan = ClanModule.getClanInfo(cid)
        if clan[9]!=1:
            return json.dumps(dict(code=3,state=clan[9],statetime=clan[10]))
        ret = ClanModule.cancelFindLeagueEnemy(cid) 
    print "cancelFindLeagueEnemy", ret
    return json.dumps(dict(code=ret))

@app.route("/beginLeagueBattle", methods=['POST'])
def beginLeagueBattle():
    cid = int(request.form.get('cid', 0))
    eid = int(request.form.get('eid', 0))
    uid = int(request.form.get('uid', 0))
    
    if not ClanModule.checkFindLeagueAuth(uid, cid):
        return json.dumps(dict(code=2))
    clan = ClanModule.getClanInfo(cid)
    if clan[9]!=0:
        return json.dumps(dict(code=3, state=clan[9], statetime=clan[10]))
    return json.dumps(dict(code=ClanModule.beginLeagueBattle(cid, eid)))

@app.route("/createClan", methods=['POST'])
def createClan():
    uid = int(request.form.get('uid', 0))
    icon = int(request.form.get('icon', 0))
    ltype = int(request.form.get('type', 0))
    name = request.form.get('name', "")
    desc = request.form.get('desc', "")
    minScore = int(request.form.get('min', 0))
    user = getUserInfos(uid)
    if user==None:
        return json.dumps(dict(clan=0))
    elif user['clan']!=0:
        clanInfo = ClanModule.getClanInfo(user['clan'])
        return json.dumps(dict(clan=0, info=list(clanInfo)))
    else:
        ret = ClanModule.createClan(uid, icon, ltype, name, desc, minScore)
    return json.dumps(dict(clan=ret, info=[ret, icon, 0, ltype, name, desc, 1, minScore, uid, 0, 0]))

@app.route("/editClan", methods=['POST'])
def editClan():
    uid = int(request.form.get('uid', 0))
    cid = int(request.form.get('cid', 0))
    icon = int(request.form.get('icon', 0))
    ltype = int(request.form.get('type', 0))
    name = request.form.get('name', "")
    desc = request.form.get('desc', "")
    minScore = int(request.form.get('min', 0))
    return json.dumps(dict(code=ClanModule.editClan(cid, icon, ltype, name, desc, minScore), name=name, desc=desc, icon=icon, type=ltype, min=minScore))

@app.route("/joinClan", methods=['POST'])
def joinClan():
    uid = int(request.form.get('uid', 0))
    cid = int(request.form.get('cid', 0))
    user = getUserInfos(uid)
    if user==None or user['clan']!=0:
        return json.dumps(dict(code=2))
    ret = ClanModule.joinClan(uid, cid)
    if ret==None:
        return json.dumps(dict(code=1))
    return json.dumps(dict(code=0, clan=ret[0], clanInfo=ret))

@app.route("/leaveClan", methods=['POST'])
def leaveClan():
    uid = int(request.form.get('uid', 0))
    cid = int(request.form.get('cid', 0))
    user = getUserInfos(uid)
    if user==None or user['clan']!=cid:
        return json.dumps(dict(code=2))
    ret = ClanModule.leaveClan(uid, cid)
    if ret==None:
        return json.dumps(dict(code=1))
    return json.dumps(dict(code=0, clan=0))

@app.route("/getLeagueBattleInfo", methods=['GET'])
def getLeagueBattleInfo():
    cid = int(request.args.get('cid', 0))
    info = ClanModule.getLeagueBattleInfo(cid)
    if info!=None:
        eid = info[1]
        if eid==cid:
            eid = info[2]
        return json.dumps(dict(code=0, info=info, clan=ClanModule.getClanInfo(eid), smembers=ClanModule.getClanMembers(cid), members=ClanModule.getClanMembers(eid)))
    return json.dumps(dict(code=1))

@app.route("/getLeagueMemberData", methods=['GET'])
def getLeagueMemberData():
    uid = int(request.args.get('uid', 0))
    euid = int(request.args.get('eid', 0))
    code = ClanModule.checkBattleWithMember(uid, euid)
    ret = dict(code=code)
    if code==0:
        ret = getUserInfos(euid)
        ret['code'] = 0
        ret['builds'] = getUserBuilds(euid)
    return json.dumps(ret)

@app.route("/clearBattleState", methods=['POST'])
def clearBattleState():
    eid = int(request.args.get('eid', 0))
    ClanModule.clearBattleStateAtOnce(eid)
    return json.dumps(dict(code=0))

@app.route("/getLeagueRank", methods=['GET'])
def getLeagueRank():
    return json.dumps(ClanModule.getTopClans())

@app.route("/synErrorLog", methods=['POST'])
def synErrorLog():
    log = request.form.get('log', "")
    uid = int(request.form.get('uid', 0))
    if uid>0 and log!="":
        update("INSERT INTO `nozomi_error_log` (uid, log) VALUES (%s,%s)", (uid, log))
    return "ok"

@app.route('/checkKeyWord', methods=['GET'])
def checkKeyWord():
    word = request.args.get('word', None, type=str)
    res = filterWord.checkWord(word, filterWord.tree)
    return jsonify(dict(res=res))
@app.route('/blockWord', methods=['GET'])
def blockWord():
    word = request.args.get('word', None, type=str)
    word = filterWord.blockWord(word)
    return jsonify(dict(word=word))

@app.route('/genRecordId', methods=['GET'])
def genRecordId():
    uid = request.args.get('uid', None, type=int)
    kind = request.args.get('kind', None, type=int)
    invoice = insertAndGetId('insert into record (uid, kind, state) values(%s, %s, %s) ', (uid, kind, 0))
    return jsonify(dict(invoice=invoice))

#客户端检测服务器上面是否有ipn 通知的数据
@app.route('/checkBuyRecord', methods=['GET'])
def checkBuyRecord():
    uid = request.args.get('uid', None, type=int)
    invoice = request.args.get('invoice', None, type=int)
    res = queryOne('select id from buyRecord where invoice = %s', (invoice))
    if res == None:
        return jsonify(dict(code=0))
    return jsonify(dict(code=1))
    
    
app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port = config.HOSTPORT)
