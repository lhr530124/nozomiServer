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
import random

from logging import Formatter
import BufferMailHandler
import util
import IpSocketHandler

from MySQLdb import cursors, connections
import redis
from werkzeug.contrib.fixers import ProxyFix

if not config.DEBUG:
    rootLogger = logging.getLogger('')
    rootLogger.setLevel(logging.INFO)
    socketHandler = IpSocketHandler.IpSocketHandler(config.LOG_HOST, config.LOG_PORT)
    rootLogger.addHandler(socketHandler)



#mysqlLogHandler = TimedRotatingFileHandler('mysqlLog.log', 'd', 1)
mysqllogger = logging.getLogger("mysqlLogger")
#mysqllogger.addHandler(mysqlLogHandler)
mysqllogger.setLevel(logging.INFO)
#mysqllogger.addHandler(mysqlLogHandler)


#oldExec = getattr(cursors.BaseCursor, 'execute')
oldQuery = getattr(connections.Connection, 'query')
    
def query(self, sql):
    mysqllogger.info("%s\n%s", sql, time.asctime())
    startTime = time.time()*1000
    oldQuery(self, sql)
    endTime = time.time()*1000


#setattr(cursor.BaseCursor, 'execute', execute)
setattr(connections.Connection, 'query', query)



reload(sys)
sys.setdefaultencoding('utf-8') 

#配置文件里面不能有注释 
#不能有其它import 之类的声明
#只能有 键值对
app = Flask(__name__)
app.config.from_object("config")

#timeLogHandler = TimedRotatingFileHandler('/data/allLog/nozomiAccess_2.log', 'd', 7)
timelogger = logging.getLogger("timeLogger")
timelogger.setLevel(logging.INFO)
#timelogger.addHandler(timeLogHandler)


@app.before_request
def beforeQuest():
    g.startTime = time.time() 
    #print request.url
@app.after_request
def afterQuest(response):
    endTime = time.time()
    timelogger.info("""
    url %s 
    args %s
    form %s
    startTime %s  
    costTime %d
    """ % (request.url, str(request.args), str(request.form), time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(g.startTime)), int((endTime-g.startTime)*10**3)) )
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

GlobalValues = [None,redis.ConnectionPool(host=config.REDIS_HOST)]
def getRedisServer(): 
    return redis.StrictRedis(connection_pool=GlobalValues[1], db=1)

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
statlogger.setLevel(logging.INFO)

loginlogger = logging.getLogger("LOGIN")
loginlogger.setLevel(logging.INFO)

crystallogger = logging.getLogger("CRYSTAL")
crystallogger.setLevel(logging.INFO)

testlogger = logging.getLogger("TEST")
testlogger.setLevel(logging.INFO)


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


@app.errorhandler(501)
def user_not_login(error):
    return redirect(url_for('login'))

platformIds = dict(ios=0,android=1,android_mm=2,android_dx=3,android_daqin=4,ios_vshare=5)

dataBuilds = [
              [1, 170018, 1, 1, 0, 1500, "{\"oil\":1000,\"food\":1000}"],
              [2, 110009, 2, 0, 0, 0, ""],
              [3, 130025, 2002, 1, 0, 400, "{\"resource\":500}"],
              [4, 180025, 1000, 1, 0, 400, ""],
              [5, 240023, 2004, 1, 0, 250, "{\"resource\":1}"],
              [6, 350003, 1003, 0, 0, 0, ""],
              [48, 140020, 7000, 1, 0, 0, ""],
              [7, 360033, 4003, 1, 0, 0, ""],
              [8, 370037, 4014, 1, 0, 0, ""],
              [9, 20002, 4003, 1, 0, 0, ""],
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
              [47, 330036, 4008, 1, 0, 0, ""]
              ]

def getUserInfos(uid):
    r = queryOne("SELECT name, score, clan, memberType, level, totalCrystal, uglevel FROM nozomi_user WHERE id=%s", (uid))
    if r==None:
        return None
    return dict(name=r[0], score=r[1], clan=r[2], mtype=r[3], level=r[4], totalCrystal=r[5], ug=r[6])

def getUserMask(uid):
    r = queryOne("SELECT mask FROM nozomi_user_mask WHERE id=%s", (uid,))
    if r==None:
        return 0
    else:
        return r[0]

def getUserAllInfos(uid):
    r = queryOne("SELECT name, score, clan, guideValue, crystal, lastSynTime, shieldTime, zombieTime, obstacleTime, memberType, totalCrystal, lastOffTime, registerTime, ban, rewardNums, magic,level,exp,cmask,hnum,uglevel FROM nozomi_user WHERE id=%s", (uid,))
    if r==None:
        return None
    return dict(name=r[0], score=r[1], clan=r[2], guide=r[3], crystal=r[4], lastSynTime=r[5], shieldTime=r[6], zombieTime=r[7], obstacleTime=r[8], mtype=r[9], totalCrystal=r[10], lastOffTime=r[11], registerTime=r[12], ban=r[13], rnum=r[14], mnum=r[15], level=r[16], exp=r[17], cmask=r[18], hnum=r[19], ug=r[20])

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
    tableName = "nozomi_build_%d" % (uid%100)
    builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM " + tableName + " WHERE id=%s AND state=0", (uid,), util.getDBID(uid))
    if builds==None or len(builds)==0:
        update("UPDATE " + tableName + " SET state=0 WHERE id=%s AND (bid<4000 or bid>=5000)",(uid,),util.getDBID(uid))
        builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM " + tableName + " WHERE id=%s AND state=0", (uid,), util.getDBID(uid))
    if builds==None or len(builds)==0:
        builds = dataBuilds
        updateUserBuilds(uid, dataBuilds)
    return builds

def deleteUserBuilds(uid, buildIndexes):
    tableName = "nozomi_build_%d" % (uid%100)
    params = []
    for bindex in buildIndexes:
        params.append([uid, bindex])
    executemany("UPDATE " + tableName + " SET state=1 WHERE id=%s AND buildIndex=%s", params, dbID=util.getDBID(uid))

def updateUserBuilds(uid, datas):
    tableName = "nozomi_build_%d" % (uid%100)
    params = []
    for data in datas:
        params.append([uid, data[0], data[1], data[2], data[3], data[4], data[5], data[6]])
    executemany("INSERT INTO " + tableName + " (id, buildIndex, grid, state, bid, level, `time`, hitpoints, extend) VALUES(%s,%s,%s,0,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE grid=VALUES(grid),state=0,bid=VALUES(bid),level=VALUES(level),`time`=VALUES(time),hitpoints=VALUES(hitpoints),extend=VALUES(extend);", params, util.getDBID(uid))

def getUserResearch(uid):
    researches = queryOne("SELECT research FROM nozomi_research WHERE id=%s", (uid))
    if researches==None:
        return [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    return json.loads(researches[0])

def updateUserResearch(uid, researches):
    update("REPLACE INTO nozomi_research (id,research) VALUES (%s,%s)", (uid, json.dumps(researches)))
    
def updateUserBuildHitpoints(uid, datas):
    tableName = "nozomi_build_%d" % (uid%100)
    params = []
    for data in datas:
        params.append([data[1], uid, data[0]])
    executemany("UPDATE " + tableName + " SET hitpoints=%s WHERE id=%s AND buildIndex=%s", params, util.getDBID(uid))

def updateUserBuildExtends(uid, datas, fixv):
    tableName = "nozomi_build_%d" % (uid%100)
    params = []
    others = []
    for data in datas:
        if data[1].find("etime")==-1 or fixv>0:
            params.append([data[1], uid, data[0]])
        else:
            others.append([data[1], uid, data[0],"%\"type\":1%"])
    executemany("UPDATE " + tableName + " SET extend=%s WHERE id=%s AND buildIndex=%s", params, util.getDBID(uid))

dailyGiftReward = [[1,1000],[1,1500],[0,5],[1,2000],[1,2500],[1,3000],[0,10],[1,3500],[1,4000],[0,15],[1,5000],[1,6500],[1,7000],[1,8000],[0,20],[1,9000],[1,10000],[1,11000],[1,12000],[0,30],[1,14000],[1,15000],[1,17000],[1,19000],[0,40],[1,23000],[1,25000],[1,27000],[1,30000],[0,50]]
dailyTaskInfos = [1,5,100,500,1,100000,1,1,1,10,1]
def newUserLogin(uid):
    today = datetime.date.today()
    ret = queryOne("SELECT regDate,loginDate,loginDays,maxLDays,curLDays,lottery,lotterySeed,dailyTask FROM `nozomi_login_new` WHERE `id`=%s", (uid))
    newGift = 0
    newLogin = False
    loginDays = 1
    curLDays = 1
    lt = 0
    lts = random.randint(10000,20000)
    dailyTasks = None
    if ret!=None:
        timedelta = (today-ret[1]).days
        if timedelta>0:
            newLogin = True
            loginDays = ret[2]+1
            maxLDays = ret[3]
            if timedelta==1:
                curLDays = ret[4]+1
                if curLDays>maxLDays:
                    maxLDays = curLDays
            newGift = curLDays
            dailyTasks = [loginDays%2, loginDays%3+2, loginDays%3+6]
            update("UPDATE `nozomi_login_new` SET loginDate=%s,loginDays=%s,maxLDays=%s,curLDays=%s,lottery=0,lotterySeed=%s,dailyTask=%s WHERE `id`=%s",(today,loginDays,maxLDays,curLDays,lts,json.dumps(dailyTasks),uid))
            update("DELETE FROM `nozomi_user_daily_task` WHERE id=%s",(uid,))
        else:
            loginDays = ret[2]
            curLDays = ret[4]
            lt = ret[5]
            lts = ret[6]
            if ret[7]!="":
                dailyTasks = json.loads(ret[7])
    else:
        newGift = 1
        newLogin = True
        update("INSERT INTO `nozomi_login_new` (`id`,regDate,loginDate,loginDays,maxLDays,curLDays,lottery,lotterySeed) VALUES(%s,%s,%s,1,1,1,0,%s)", (uid, today, today, lts))
    if newGift>0:
        reward = dailyGiftReward[(newGift-1)%30]
        update("DELETE FROM `nozomi_reward_new` WHERE uid=%s AND `type`=%s", (uid,1))
        update("INSERT INTO `nozomi_reward_new` (uid,`type`,`rtype`,`rvalue`,`info`) VALUES(%s,%s,%s,%s,%s)", (uid,1,reward[0],reward[1],json.dumps(dict(day=newGift))))
    if dailyTasks!=None:
        taskDict = dict()
        taskList = []
        for i in range(len(dailyTasks)):
            tid = dailyTasks[i]
            taskList.append([tid,0,dailyTaskInfos[tid]])
            taskDict[tid] = i
        if not newLogin:
            tasks = queryAll("SELECT tid,num FROM `nozomi_user_daily_task` WHERE id=%s",(uid,))
            if tasks!=None:
                for task in tasks:
                    if task[0] in taskDict:
                        taskList[taskDict[task[0]]][1] = task[1]
        dailyTasks = taskList
    return [0, loginDays, curLDays, newLogin, lt, lts, dailyTasks]

def getUserRewardsNew(uid):
    allRewards = queryAll("SELECT `id`,`type`,`rtype`,`rvalue`,`info` FROM `nozomi_reward_new` WHERE uid=%s", (uid))
    if allRewards!=None and len(allRewards)>0:
        return allRewards
    else:
        return []

def deleteUserRewards(rwList):
    executemany("DELETE FROM `nozomi_reward_new` WHERE id=%s", [(k,) for k in rwList])

def updatePurchaseCrystal(uid, crystal, ctype):
    if ctype>4:
        update("UPDATE `nozomi_user` SET totalCrystal=totalCrystal+%s, lastOffTime=%s WHERE id=%s", (crystal, time.mktime(time.localtime()), uid))
    else:
        update("UPDATE `nozomi_user` SET totalCrystal=totalCrystal+%s WHERE id=%s", (crystal, uid))

platformIds = dict(ios=0, android=1, android_our=2, android_german=3, ios_cn=4)

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
        try:
            return json.dumps([[json.loads(r[0]), r[1], r[2], r[3], r[4]] for r in ret])
        except Exception as e:
            app.logger.exception('''
            url %s
            args %s
            form %s
            ''' % (request.url, str(request.args), str(request.form)))
            return "[]"

InviteRewards = [[10,5],[20,100,50],[100,500,250],[500,1000,500]]

@app.route("/addInviteRewards", methods=['POST'])
def addInviteRewards():
    uid = request.form.get("uid",0,type=int)
    level = request.form.get("level",0,type=int)
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT rlv, tr FROM nozomi_invite_stat WHERE id=%s",(uid,))
    res = cur.fetchone()
    rserver = getRedisServer()
    ret = dict(code=0, level=level)
    ireward = None
    if level<len(InviteRewards):
        ireward = InviteRewards[level]
    if res!=None and ireward!=None and res[0]==level-1 and res[1]>=ireward[0]:
        cur.execute("UPDATE nozomi_invite_stat SET rlv=%s WHERE id=%s",(level,uid))
        rwds = []
        ccid = rserver.incr("rwdServer")
        cur.execute("INSERT INTO nozomi_reward_new (id,uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s,%s)",(ccid,uid,4,0,ireward[1],''))
        rwds.append([ccid,4,0,ireward[1],''])
        ccid = rserver.incr("rwdServer")
        cur.execute("INSERT INTO nozomi_reward_new (id,uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s,%s)",(ccid,uid,4,3,ireward[2],''))
        rwds.append([ccid,4,3,ireward[2],''])
        ret['rewards'] = rwds
        con.commit()
    elif res!=None:
        ret['level'] = res[0]
        ccid = rserver.get("rwdServer")
        if ccid!=None:
            ccid = int(ccid)
            cur.execute("SELECT `id`,`type`,`rtype`,`rvalue`,`info` FROM `nozomi_reward_new` WHERE uid=%s AND id<=%s", (uid,ccid))
            rwds = cur.fetchall()
            if rwds!=None:
                ret['rewards'] = rwds
    cur.close()
    return json.dumps(ret)

@app.route("/inviteUser", methods=['POST'])
def inviteUser():
    uid = request.form.get("uid",0,type=int)
    rid = request.form.get("rid",0,type=int)
    ret = dict(code=0)
    con = getConn()
    cur = con.cursor()
    nt = time.localtime()
    ctime = int(time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 )))
    cur.execute("SELECT itime FROM nozomi_invite_record WHERE sid=%s AND itime>=%s LIMIT 1",(uid,ctime))
    res = cur.fetchone()
    if res==None:
        errorCode = 0
        cur.execute("SELECT id,name,ban FROM nozomi_user WHERE id=%s",(rid,))
        res = cur.fetchone()
        if res==None:
            errorCode = 2
        else:
            cur.execute("SELECT itime FROM nozomi_invite_record WHERE sid=%s AND rid=%s",(uid,rid))
            res = cur.fetchone()
            if res!=None:
                errorCode = 3
        if errorCode==0:
            cur.execute("SELECT ts FROM nozomi_invite_stat WHERE id=%s",(uid,))
            res = cur.fetchone()
            if res==None:
                cur.execute("INSERT INTO nozomi_invite_stat (id,ts,tg,tr,rlv) VALUES (%s,1,0,0,0) ON DUPLICATE KEY update ts=ts+1",(uid,))
            else:
                cur.execute("UPDATE nozomi_invite_stat SET ts=ts+1 WHERE id=%s",(uid,))
            cur.execute("SELECT tr FROM nozomi_invite_stat WHERE id=%s",(rid,))
            res = cur.fetchone()
            if res==None:
                cur.execute("INSERT INTO nozomi_invite_stat (id,ts,tg,tr,rlv) VALUES (%s,0,0,1,0) ON DUPLICATE KEY update tr=tr+1",(rid,))
            else:
                cur.execute("UPDATE nozomi_invite_stat SET tr=tr+1 WHERE id=%s",(rid,))
            ctime = int(time.mktime(nt))
            cur.execute("INSERT INTO nozomi_invite_record (sid,rid,itime) VALUES (%s,%s,%s)",(uid,rid,ctime))
            con.commit()
            ret['ltime'] = ctime
        else:
            ret['subcode'] = errorCode
    else:
        ret['ltime'] = res[0]
        ret['subcode'] = 1
    cur.close()
    return json.dumps(ret)

@app.route("/getInviteRecord", methods=['GET'])
def getInviteRecord():
    uid = request.args.get("uid",0,type=int)
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT ts, tg, tr, rlv FROM nozomi_invite_stat WHERE id=%s",(uid,))
    res = cur.fetchone()
    if res==None:
        res = [0,0,0,0,0]
    ret = dict(code=0, stat=res, one=InviteRewards[0], levels=InviteRewards[1:])
    nt = time.localtime()
    ctime = int(time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 )))
    if res[0]>0:
        cur.execute("SELECT itime FROM nozomi_invite_record WHERE sid=%s AND itime>=%s LIMIT 1",(uid,ctime))
        res2 = cur.fetchone()
        if res2==None:
            ret['ltime'] = ctime-1
        else:
            ret['ltime'] = res2[0]
    if res[2]>0:
        cur.execute("SELECT u.name,u.level,u.totalCrystal,r.itime FROM nozomi_user AS u, nozomi_invite_record AS r WHERE r.rid=%s AND r.sid=u.id ORDER BY r.itime DESC LIMIT 20", (uid,))
        ret['records'] = cur.fetchall()
        cur.execute("SELECT u.name,u.level,u.totalCrystal,r.itime FROM nozomi_user AS u, nozomi_invite_record AS r WHERE r.sid=%s AND r.rid=u.id ORDER BY r.itime DESC LIMIT 20", (uid,))
        ret['srecords'] = cur.fetchall()
    cur.close()
    return json.dumps(ret)

cbTimes = [82800, 86400,3,1419644150]
def getClanBoss(cid):
    ret = None
    if cid>0:
        ret = queryOne("SELECT n1time,n2time,mstage,cstage,chp FROM nozomi_league_boss WHERE id=%s",(cid,))
    else:
        return None
    tt = cbTimes[0]
    if ret==None:
        t = int(time.time())
        while cbTimes[3]<t:
            cbTimes[3] += cbTimes[1]
        t1 = cbTimes[3]
        t2 = cbTimes[3]+cbTimes[1]
        ret = [t1,t2,0,0,0]
        update("INSERT IGNORE INTO nozomi_league_boss (id,n1time,n2time,mstage,cstage,chp) VALUES (%s,%s,%s,0,0,0)",(cid,t1,t2))
    return [ret[0],ret[0]+tt,ret[1],ret[2],ret[3],ret[4]]

@app.route("/getClanBossData", methods=['GET'])
def getClanBossData():
    cid = request.args.get('cid',0,type=int)
    ret = dict(code=0)
    if cid>0:
        ret['cbe'] = getClanBoss(cid)
        ret['rusers'] = queryAll("SELECT u.id,u.name,if(cu.hp is NULL,0,cu.hp),u.score,if(cu.chance is NULL,%s,cu.chance) FROM nozomi_user AS u LEFT JOIN nozomi_league_boss_member AS cu ON cu.id=u.id WHERE u.clan=%s ORDER BY u.score DESC",(3,cid))
    return json.dumps(ret)

@app.route("/challengeBoss", methods=['POST'])
def challengeClanBoss():
    cid = request.form.get("cid",0,type=int)
    uid = request.form.get("uid",0,type=int)
    sid = request.form.get("sid",0,type=int)
    cdata = getClanBoss(cid)
    lhp = 0
    ret = dict(code=0, cbe=cdata, sid=sid)
    if cdata==None:
        ret['code'] = 1
        ret['sid'] = 0
    elif cdata[4]==0:
        bhps = [1000000,5000000,22500000,50000000]
        lhp = bhps[sid-1]
        update("UPDATE nozomi_league_boss SET cstage=%s, chp=%s WHERE id=%s",(sid,lhp,cid))
    elif cdata[4]==sid:
        lhp = cdata[5]
        if lhp<=0:
            ret['code'] = 2
        else:
            ret['sid'] = sid
    else:
        ret['code'] = 1
        ret['sid'] = cdata[4]
    if ret['code']==0:
        ret['hp'] = lhp
    return json.dumps(ret)

@app.route("/synBossBattle", methods=['POST'])
def synBossBattle():
    uid = request.form.get("uid",0,type=int)
    cid = request.form.get("cid",0,type=int)
    hp = request.form.get("hp",0,type=int)
    update("INSERT INTO nozomi_league_boss_member (id,hp,chance) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE hp=hp+VALUES(hp), chance=if(chance>1,chance-1,0)",(uid,hp,2))
    update("UPDATE nozomi_league_boss SET chp=if(chp>%s,chp-%s,0) WHERE id=%s",(hp,hp,cid))
    return json.dumps(dict(code=0, cbe=getClanBoss(cid)))

codeNames = {20151:"2a1",20153:"2a2",20155:"2a3",20157:"2b1",20159:"2b2",20161:"2b3",20163:"2c1",20165:"2c2",20167:"2c3",20169:"3a2",20171:"3a1",20173:"3a3",20175:"3b1",20177:"3b2",20179:"3b3",20181:"3c1",20183:"3c2",20185:"3c3",20187:"4a1",20189:"4a2",20191:"4b1",20193:"4a3",20195:"4b2",20197:"4b3",20199:"4c1",20201:"4c2",20203:"4c3",20205:"5a3",20207:"5a1",20211:"5a2",20213:"5b1",20215:"5b2",20217:"5b3",20219:"5c1",20221:"5c2",20223:"5c3",20225:"6a2",20227:"6a1",20229:"6c1",20231:"6b3",20233:"6a3",20235:"6b1",20237:"6c2",20239:"6b2",20243:"6c3",20245:"7a3",20247:"7b1",20249:"7b2",20251:"7a2",20253:"7c1",20255:"7a1",20257:"7b3",20259:"7c3",20261:"7c2",20263:"8a3",20265:"8b1",20267:"8b3",20269:"8a2",20271:"8b2",20273:"8a1",20275:"8c3",20277:"8c2",20279:"8c1",20281:"9b3",20283:"9c1",20285:"9a3",20287:"9a2",20289:"9a1",20291:"9b1",20293:"9b2",20295:"9c3",20297:"9c2",20299:"10b2",20301:"10b3",20303:"10a2",20305:"10c2",20307:"10a3",20309:"10a1",20311:"10b1",20313:"10c1",20315:"10c3",20317:"2c1",20319:"2b1",20321:"2a1",20323:"2c2",20325:"2b2",20327:"2a2",20329:"2c3",20331:"2b3",20333:"2a3",20335:"3c1",20337:"3b1",20339:"3a2",20341:"3c2",20343:"3b2",20345:"3a1",20347:"3c3",20349:"3b3",20351:"3a3",20353:"4c1",20355:"4a3",20357:"4a1",20359:"4c2",20361:"4b2",20363:"4a2",20365:"4c3",20367:"4b3",20369:"4b1",20371:"5c1",20375:"5b1",20377:"5a3",20379:"5c2",20381:"5b2",20383:"5a1",20385:"5c3",20387:"5b3",20389:"5a2",20391:"6c2",20393:"6b3",20395:"6a2",20397:"6b2",20399:"6a3",20401:"6a1",20403:"6c3",20405:"6b1",20407:"6c1",20409:"7b3",20411:"7a2",20413:"7a3",20415:"7c3",20417:"7c1",20419:"7b1",20421:"7c2",20423:"7a1",20425:"7b2",20427:"8c3",20429:"8a2",20431:"8a3",20433:"8c2",20435:"8b2",20437:"8b1",20439:"8c1",20441:"8a1",20443:"8b3",20445:"9b2",20447:"9a2",20449:"9b3",20451:"9c3",20453:"9a1",20455:"9c1",20457:"9c2",20459:"9b1",20461:"9a3",20463:"10b1",20465:"10c2",20467:"10b2",20469:"10c1",20471:"10a3",20473:"10b3",20475:"10c3",20477:"10a1",20479:"10a2"}

def redisLock(rserver, lk):
    lv = rserver.incr(lk)
    rserver.expire(lk,20)
    lktick = 10
    while lv>1 and lktick>0:
        rserver.decr(lk)
        time.sleep(0.5)
        lktick -= 1
        lv = rserver.incr(lk)
    if lktick==0:
        print("death lock in key:%s?" % lk)
        testlogger.info("death lock in key:%s?" % lk)
        rserver.setex(lk,20,1)

def redisUnlock(rserver, lk):
    rserver.decr(lk)

def newInitUser(uid,plat,device,curTime):
    con = getConn()
    cur = con.cursor()

    platformId = platformIds.get(plat, 0)
    cur.execute("INSERT INTO nozomi_user (id, lastSynTime, name, registerTime, score, crystal, shieldTime, platform, lastOffTime, magic, level) VALUES(%s, %s, %s, %s, 0, %s, 0, %s, %s, 100, 1)", (uid, curTime, "", curTime, 500, platformId, curTime))
    cur.execute("REPLACE INTO nozomi_rank (uid, score) VALUES (%s, %s)",(uid, 0))
    cur.execute("REPLACE INTO nozomi_research (id, research) VALUES(%s, '[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]')", (uid,))
    cur.execute("REPLACE INTO nozomi_user_state (uid, score, shieldTime, onlineTime, attackTime) VALUES (%s, %s, 0, 0, 0)", (uid, 0))
    params = []
    for i in range(1, 23):
        params.append([uid, i])
    cur.executemany("INSERT IGNORE INTO nozomi_achievement (uid, achieve, level, num) VALUES (%s,%s,1,0)",params)
    con.commit()
    cur.close()
    updateUserBuilds(uid, dataBuilds)
    loginlogger.info("%s\t%d\treg\t%s" % (plat,uid,device))
    
    return dict(name="", score=0, clan=0, guide=0, crystal=500, lastSynTime=curTime, shieldTime=0, zombieTime=0, obstacleTime=0, mtype=0, totalCrystal=0, lastOffTime=curTime, registerTime=curTime, ban=0, rnum=0, mnum=100, level=1, exp=0, cmask=0, hnum=0, ug=0)

updateUrls = {'other': 'https://itunes.apple.com/app/id915963054', 'com.caesars.zclash': 'https://play.google.com/store/apps/details?id=com.caesars.zclash', 'com.caesars.nozomi': 'https://play.google.com/store/apps/details?id=com.caesars.nozomi', 'com.caesars.caesars': 'https://play.google.com/store/apps/details?id=com.caesars.nozomi', 'com.caesars.clashzombie': 'https://itunes.apple.com/app/id915963054', 'com.caesars.empire': 'https://itunes.apple.com/app/id608847384'}
settings = [17,int(time.mktime((2014,9,1,12,0,0,0,0,0)))-util.beginTime, True, int(time.mktime((2013,11,26,6,0,0,0,0,0)))-util.beginTime,17]
newActivitys2 = [[1422057600,1422144000,"act4",30,64,86400*14],[1422057600,1422144000,"act1",0,8,86400*14,1],[1422057600,1422144000,"act3",30,32,86400*14],[1422057600,1422144000,"act8",10,1024,86400*7]]
newActivitys3 = [[1421452800,1421539200,"act2",30,16,86400*14],[1421452800,1421539200,"act1",0,8,86400*14,0],[1421452800,1421539200,"act4",30,64,86400*14,"special"],[1421452800,1421539200,"act8",10,1024,86400*7]]
stours = [] #[1,1,0,2,1422230400,604800,1800,432000,489600,547200]]
@app.route("/getData", methods=['GET'])
def getData():
    uid = int(request.args.get("uid"))
    data = None
    if "login" in request.args:
        version = request.args.get("version", 0, type=int)
        platform = "ios"
        if 'platform' in request.args:
            platform = request.args['platform']
        language = 0
        if platform=="ios_cn":
            language=1
        if 'language' in request.args:
            language = request.args['language']
        sversion = request.args.get("scriptVersion",1,type=int)
        lang = request.args.get("lang","US")
        cc = request.args.get("cc","")
        ret = None
        shouldDebug = False
        if 'v2' not in request.args:
            country = request.args.get('country',"us").lower()
            if country=="":
                country = "us"
            ret = dict(serverUpdate=1)
            if language==0:
                ret['title'] = "Big Update!"
                ret['content']="More updates in the near future, welcome to feedback!"
                ret['button1']="Update"
                ret['button2']="Later"
            else:
                ret['title'] = "新版本来啦！"
                ret['content'] = "1. 上线了英雄系统；\n2. 上线了神像系统；\n3. 调整了人口相关数值；\n4. 优化了联盟战斗、僵尸攻打机制。"
                ret['button1']="立即更新"
                ret['button2']="稍后更新"
            if platform.find("android")==0:
                ret['url'] = "https://play.google.com/store/apps/details?id=com.caesars.nozomi"
            else:
                ret['url'] = "https://itunes.apple.com/app/id608847384?mt=8&uo=4"
            ret['forceUpdate']=1
            return json.dumps(ret)
        else:
            checkVersion = request.args.get("checkVersion", 0, type=int)
            if checkVersion>settings[0] and platform.find("android")==-1:
                shouldDebug = True
            elif checkVersion<settings[0]:
                stitle = "New Version!"
                stext = "A big update is coming! New heroes, new features are waiting for you!"
                sbut1 = "Update Now"
                sbut2 = "Later"
                if lang=="CN":
                    stitle = "新版本来啦！"
                    stext = "一个大更新版本来啦！新英雄，新功能在等着你！"
                    sbut1 = "现在更新"
                    sbut2 = "以后更新"
                elif lang=="HK":
                    stitle = "新版本來啦！"
                    stext = "壹個大更新版本來啦！新英雄，新功能在等著你！"
                    sbut1 = "現在更新"
                    sbut2 = "以後更新"
                ret = dict(serverUpdate=1, title=stitle, content=stext, button1=sbut1, button2=sbut2)
                if cc!="":
                    ret['url'] = updateUrls[cc.strip("0123456789")]
                elif platform.find("android")==0:
                    ret['url'] = "https://play.google.com/store/apps/details?id=com.caesars.nozomi"
                else:
                    ret['url'] = "https://itunes.apple.com/app/id608847384?mt=8&uo=4"
                if settings[2]:
                    ret['forceUpdate'] = 1
                    return json.dumps(ret)
        if sversion<settings[4]:
            stitle = "New Version!"
            stext = "Big update of Nozomi, tap Close and relogin game please!"
            sbut = "Close"
            if lang=="CN":
                stitle = "新版本来啦！"
                stext = "希望号升级了许多新功能，请点击关闭重启游戏以进行更新！"
                sbut = "关闭"
            elif lang=="HK":
                stitle = "新版本來啦！"
                stext = "希望號升級了許多新功能，請點擊關閉重啓遊戲以進行更新！"
                sbut = "關閉"
            return json.dumps(dict(serverError=1, title=stitle, content=stext, button=sbut))
        data = getUserAllInfos(uid)
        deviceId = ""
        t = int(time.mktime(time.localtime()))
        if 'cdev' in request.args:
            deviceId = request.args['cdev']
        if data==None:
            data = newInitUser(uid,platform,deviceId,t)
        elif data['ban']!=0:
            ret = dict(serverError=1)
            if lang=="CN":
                ret['title'] = "你被封禁了！"
                ret['content'] = "你因为修改数据而被封禁了账号！请联系feedback@caesarsgame.com进行解封！"
                ret['button'] = "关闭"
            elif lang=="HK":
                ret['title'] = "你被封禁了！"
                ret['content'] = "你因爲修改數據而被封禁了賬號！請聯系feedback@caesarsgame.com進行解封！"
                ret['button'] = "關閉"
            else:
                ret['title'] = "You are banned!"
                ret['content'] = "You are banned because of the hacked data! Please contact feedback@caesarsgame.com to unban your account!"
                ret['button'] = "Close"
            return json.dumps(ret)
        else:
            state = getUserState(uid)
            if 'attackTime' in state:
                return json.dumps(state)
        if data['cmask']>0:
            ret = dict(serverUpdate=1)
            forceUpdate = False
            if cc.find("com.caesars.empire")==0:
                ret['url'] = "https://itunes.apple.com/app/id915963054?mt=8&uo=4"
                forceUpdate = True
            elif cc.find("com.caesars.nozomi")==0 or cc.find("com.caesars.caesars")==0:
                ret['url'] = "https://play.google.com/store/apps/details?id=com.caesars.zclash"
                forceUpdate = True
            elif data['cmask']>1:
                update("UPDATE nozomi_user SET cmask=1 WHERE id=%s",(uid,))
                info = dict(nos=1)
                if lang=="CN":
                    info['title'] = "感谢你的更新！"
                    info['text'] = "感谢你更新了新版本！我们给予了你500水晶作为奖励！"
                elif lang=="HK":
                    info['title'] = "感謝你的更新！"
                    info['text'] = "感謝你更新了新版本！我們給予了你500水晶作爲獎勵！"
                else:
                    info['title'] = "Thanks for update!"
                    info['text'] = "Thanks for update our new version! We send you 500 crystals as reward!"
                update("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)",(uid,3,0,500,json.dumps(info)))
            if forceUpdate:
                ret['forceUpdate'] = 1
                ret['button2'] = ""
                ret['cmask'] = data['cmask']
                if lang=="CN":
                    ret['title'] = "请更新版本！"
                    ret['content'] = "十分抱歉，由于服务器原因，需要您下载版本。您的数据将不会改变，进入新版本后您将获得500水晶补偿。"
                    ret['button1'] = "下载"
                elif lang=="HK":
                    ret['title'] = "請更新版本！"
                    ret['content'] = "十分抱歉，由于服務器原因，需要您下載版本。您的數據將不會改變，進入新版本後您將獲得500水晶補償。"
                    ret['button1'] = "下載"
                else:
                    ret['title'] = "Update New Version!"
                    ret['content'] = "Sorry, you need download a new version because of server's problem. Your data won't be changed and you will get 500 Crystals as compensation."
                    ret['button1'] = "Download"
                testlogger.info("%s\t%d\tlogin\t%s\t%s" % (platform,uid,cc,deviceId))
                return json.dumps(ret)
            else:
                ret = None
        if ret!=None:
            data.update(ret)
        data['serverTime'] = t
        if shouldDebug:
            data['payDebug'] = 1
        data['rtime'] = util.getRankTime(t,0)
        if data['lastSynTime']==0:
            data['lastSynTime'] = data['serverTime']
        data['achieves'] = achieveModule.getAchieves(uid)
        loginResult = newUserLogin(uid)
        data['leftDay'] = loginResult[0]
        data['ldays'] = loginResult[1]
        data['cdays'] = loginResult[2]
        if loginResult[3]:
            data['newlogin'] = 1
        data['lt'] = loginResult[4]
        data['lts'] = loginResult[5]
        data['dtasks'] = loginResult[6]
        data['newRewards'] = getUserRewardsNew(uid)
        data['mask'] = getUserMask(uid)
        zdc = queryOne("SELECT chance,stage,etime FROM nozomi_zombie_challenge WHERE id=%s",(uid,))
        if zdc!=None:
            data['zdc'] = zdc
        stages = queryAll("SELECT stars,lres FROM nozomi_stages WHERE id=%s ORDER BY sid",(uid,))
        if stages!=None:
            data['stages'] = stages
        data['nacts'] = newActivitys2
        data['tours'] = stours
        data['utours'] = queryAll("SELECT tid,tstage,trank,ttype,star FROM nozomi_user_tour WHERE id=%s",(uid,))
        objs = queryOne("SELECT objs FROM nozomi_user_objs WHERE id=%s AND id2=0",(uid,))
        if objs==None:
            objs = []
        else:
            objs = json.loads(objs[0])
        data['objs'] = objs
        zdt = queryOne("SELECT chance,stage,etime,hp FROM nozomi_boss_challenge WHERE id=%s",(uid,))
        if zdt!=None:
            data['zdt'] = zdt
        if data['clan']>0:
            carena = queryOne("SELECT state,btime,battlers FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(data['clan'],1))
            if carena!=None:
                data['arena1'] = carena
            data['cbe'] = getClanBoss(data['clan'])
        arenas = queryAll("SELECT state,btime,atype FROM nozomi_arena_prepare WHERE id=%s AND atype>=%s",(uid,2))
        if arenas!=None and len(arenas)>0:
            for ainfo in arenas:
                data['arena%d' % ainfo[2]] = [ainfo[0], ainfo[1]]
        if data['guide']>=1400:
            data['ng2'] = queryAll("SELECT etime,num FROM nozomi_user_gift2 WHERE id=%s",(uid,))
        rserver = getRedisServer()
        rid = random.randint(0, 1000000) 
        data['treq'] = rid
        rserver.setex("utoken%d" % uid, 3600, rid)
        loginlogger.info("%s\t%d\tlogin\t%d\t%s" % (platform,uid,rid,deviceId))
    else:
        data = getUserInfos(uid)
    if data==None:
        return json.dumps(dict(serverError=1, title="User was deleted!", content="This user was deleted!", button="Close"))
    if data['clan']>0:
        data['clanInfo'] = ClanModule.getClanInfo(data['clan'])
    #data['builds'] = getUserBuilds(uid)
    data['researches'] = getUserResearch(uid)
    #fix data
    repairDatas = []
    builds = getUserBuilds(uid)
    builds = [list(r) for r in builds]
    builders = []
    errorBuilderNum = 0
    for build in builds:
        if build[2]==2004:
            try:
                check = json.loads(build[6])
                if check['resource'] == 0:
                    errorBuilderNum = errorBuilderNum+1
                    builders.append(build)
            except e:
                print e
        elif build[4]>0:
            errorBuilderNum = errorBuilderNum-1
    while errorBuilderNum>0:
        errorBuilderNum = errorBuilderNum-1
        builders[errorBuilderNum][6]='{"resource":1}'
        repairDatas.append([builders[errorBuilderNum][0],'{"resource":1}'])
    if len(repairDatas)>0:
        testlogger.info("repair data %d:%s" % (uid, json.dumps(repairDatas)))
        if 'login' in request.args:
            updateUserBuildExtends(uid, repairDatas,1)
    data['builds']=builds
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
        updateUserAttack(eid)
        if data['clan']>0:
            data['clanInfo'] = ClanModule.getClanInfo(data['clan'])
        data['builds'] = getUserBuilds(eid)
        data['code'] = 0
        return json.dumps(data)

@app.route("/getReplay", methods=['GET'])
def getReplay():
    vid = int(request.args.get("vid"))
    return queryOne("SELECT replay FROM nozomi_replay WHERE id=%s", (vid))[0]

resourceMap={2004:1, 2001:2000000, 2003:2000000, 2005:80000}
maxList = [[0,4],[1,1],[2,1],[1000,4],[1001,4],[1002,1],[1003,1],[1004,1],[1005,1],[2000,7],[2001,4],[2002,7],[2003,4],[2004,5],[2005,4],[3000,6],[3001,7],[3002,3],[3003,4],[3004,4],[3005,4],[3006,250],[3007,3]]

def checkBuilds(uid, updateBuilds, deleteBuilds, accTimes):
    oldBuilds = getUserBuilds(uid)
    buildsMap = dict()
    countMap = dict()
    for build in oldBuilds:
        buildsMap[build[0]] = build
        countMap[build[2]] = countMap.get(build[2],0)+1
    for bid in deleteBuilds:
        if bid in buildsMap:
            build = buildsMap.pop(bid)
            countMap[build[2]] = countMap[build[2]]-1
    ret = 0
    try:
        etime = int(time.mktime(time.localtime()))+60
        for build in updateBuilds:
            x = build[1]/10000
            y = build[1]%10000
            if x<1 or x>40 or y>40:
                ret = 1
                break
            oldBuild = buildsMap.get(build[0])
            if oldBuild!=None:
                if oldBuild[2]!=build[2]:
                    if oldBuild[2]<4000 and oldBuild[3]>0:
                        ret = 2
                        break
                    countMap[oldBuild[2]] = countMap[oldBuild[2]]-1
                    countMap[build[2]] = countMap.get(build[2],0)+1
                elif build[2]<6000 and build[3]>oldBuild[3] and build[2]!=3006:
                    dis = build[3]-oldBuild[3]
                    if oldBuild[3]<=3:
                        dis -= (3-oldBuild[3])
                    if dis>0 and oldBuild[4]>0:
                        dis -= 1
                    accTimes = accTimes-dis
                    if accTimes<0:
                        ret = 3
                        break
            if build[6]!="":
                checkExt = json.loads(build[6])
                if build[2]==1005:
                    if 'weapons' in checkExt:
                        weapons = checkExt['weapons']
                        tw = 0
                        for n in weapons:
                            tw += n
                        if tw>5:
                            ret = 4
                            break
                elif build[2]==1000 or build[2]==1004:
                    if 'soldiers' in checkExt:
                        soldiers = checkExt['soldiers']
                        tn = 0
                        for n in soldiers:
                            tn+=n
                        if tn>300:
                            ret = 10
                            break
                elif build[2]==1001:
                    if 'callList' in checkExt:
                        callList = checkExt['callList']
                        for callItem in callList:
                            if callItem[0]>build[3] or callItem[1]>100:
                                ret = 5
                                break
                        if ret>0:
                            break
                elif build[2]==1:
                    if checkExt.get('oil',0)>1000 or checkExt.get('food',0)>1000:
                        ret = 6
                        break
                elif build[2] in resourceMap:
                    if checkExt.get('resource',0)>resourceMap[build[2]]:
                        ret = 6
                        break
    except:
        ret = 7
    if ret==2:
        return True
    elif ret==10:
        tableName = "nozomi_build_%d" % (uid%100)
        update("UPDATE " + tableName + " SET extend=%s WHERE id=%s AND bid=1000",('{"soldiers":[0,0,0,0,0,0,0,0,0,0,0,0]}',uid),util.getDBID(uid))
        return True
    if ret==0:
        for pair in maxList:
            if countMap.get(pair[0],0)>pair[1]:
                ret = 8
                break
    if ret>0:
        if ret!=2:
            update("UPDATE nozomi_user SET ban=2 WHERE id=%s",(uid))
            testlogger.info("banUserId:%d,banType:%d,requestBuilds:%s" % (uid, ret, json.dumps(updateBuilds)))
        return True
    else:
        return False

@app.route("/synData", methods=['POST'])
def synData():
    uid = int(request.form.get("uid", 0))
    if uid==0:
        return json.dumps({'code':2})
    if 'req' in request.form:
        rserver = getRedisServer()
        rid = rserver.get("utoken%d" % uid)
        if rid!=None:
            rid = int(rid)
            nrid = request.form.get('req',0,type=int)
            if nrid>rid or nrid<rid-3:
                print("token error, may be login in two device", uid)
                return json.dumps({'code':2,'subcode':1})
            elif nrid<rid:
                print("token the same, may be syn data twice", uid)
                return json.dumps(dict(code=0,subcode=0))
            else:
                rid += 1
                rserver.setex("utoken%d" % uid, 7200, rid)
        else:
            print("token out date",uid)
            return json.dumps({'code':2})
    platform = "ios"
    if 'platform' in request.form:
        platform = request.form['platform']
    #TODO deleted in the next version
    if 'servertime' in request.form:
        stime = request.form.get('servertime', 0, type=int)
        ctime = int(time.mktime(time.localtime()))
        if stime<ctime-600 or stime>ctime+600:
            return '{"code":2}'
    accTimes = 0
    if 'crystal' in request.form:
        ls = json.loads(request.form['crystal'])
        for l in ls:
            if l[0]>0:
                crystallogger.info("%s\t%d\t%s" % (platform, uid, json.dumps(l)))
                if l[0]==1:
                    accTimes=accTimes+1
                elif l[0]==4 and l[2]<1:
                    update("UPDATE nozomi_user SET ban=2 WHERE id=%s",(uid))
                    testlogger.info("banUserId:%d,banType:%d,requestCrystals:%s" % (uid, 9, json.dumps(ls)))
                    return '{"code":1}'
    deleteBuilds = []
    if 'delete' in request.form:
        deleteBuilds = json.loads(request.form['delete'])
        if 1 in deleteBuilds:
            deleteBuilds = []
    updateBuilds = request.form.get("update")
    if updateBuilds!=None:
        try:
            updateBuilds = json.loads(updateBuilds)
        except:
            return '{"code":2}'
        if checkBuilds(uid,updateBuilds,deleteBuilds,accTimes):
            return '{"code":1}'
    userDbInfo = getUserAllInfos(uid)
    if userDbInfo==None or userDbInfo['ban']!=0:
        return '{"code":1}'
    if 'cmds' in request.form:
        cmds = json.loads(request.form['cmds'])
        baseTime = cmds[0]
        ctime = int(time.time())
        zdc = queryOne("SELECT chance,stage,etime FROM nozomi_zombie_challenge WHERE id=%s",(uid,))
        if zdc==None:
            zdc = [5,0,0]
        else:
            zdc = list(zdc)
            while zdc[0]<5 and zdc[2]<ctime:
                zdc[0] += 1
                zdc[2] += 7200
        zchanged = False
        for cmd in cmds[1]:
            cmdTime = baseTime+cmd[1]
            cmdInfo = cmd[2]
            if cmd[0]==1:
                alevel = 0
                if cmdInfo[1]>=3:
                    alevel = cmdInfo[0]*10
                UserRankModule.updateZombieCount(uid, cmdInfo[2])
                zdc[0] -= 1
                if alevel>zdc[1]:
                    zdc[1] = alevel
                print "Syn Batch Time",zdc[0],zdc[2],baseTime,cmd[1]
                if zdc[0]<5 and zdc[2]<cmdTime:
                    zdc[2] = cmdTime+7200
                zchanged = True
            elif cmd[0]==2:
                if cmdInfo[0]==1:
                    zdc[0] += cmdInfo[1]
                    zchanged = True
        if zchanged:
            update("REPLACE INTO nozomi_zombie_challenge (id,chance,stage,etime) VALUES (%s,%s,%s,%s)",(uid,zdc[0],zdc[1],zdc[2]))
    if 'objs' in request.form:
        update("REPLACE INTO nozomi_user_objs (id,id2,objs) VALUES (%s,0,%s)",(uid, request.form['objs']))
    if 'zdt' in request.form:
        zdt = json.loads(request.form['zdt'])
        update("REPLACE INTO nozomi_boss_challenge (id,chance,stage,etime,hp) VALUES (%s,%s,%s,%s,%s)",(uid,zdt[0],zdt[1],zdt[2],zdt[3]))
    if 'lts' in request.form:
        lts = json.loads(request.form['lts'])
        update("UPDATE nozomi_login_new SET lottery=%s, lotterySeed=%s WHERE id=%s",(lts[0],lts[1],uid))
    if 'dtp' in request.form:
        params = [[uid,r[0],r[1]] for r in json.loads(request.form['dtp'])]
        executemany("REPLACE INTO nozomi_user_daily_task (id,tid,num) VALUES (%s,%s,%s)",params)
    if 'dtg' in request.form:
        update("UPDATE nozomi_login_new SET dailyTask=%s WHERE id=%s",("",uid))
    if 'irn' in request.form:
        update("UPDATE nozomi_invite_stat SET tg=tg+%s WHERE id=%s",(request.form.get("irn",0,type=int), uid))
    userInfoUpdate = dict(lastSynTime=int(time.mktime(time.localtime())))
    if 'userInfo' in request.form:
        userInfo = json.loads(request.form['userInfo'])
        userInfoUpdate.update(userInfo)
        if 'score' in userInfo:
            userInfoUpdate.pop('score')
        if 'shieldTime' in userInfo:
            setUserShield(uid, userInfo['shieldTime'])
    changeCrystal = 0
    oldCrystal = userDbInfo['crystal']
    newCrystal = oldCrystal
    if 'cc' in request.form:
        baseCrystal = request.form.get('bs',0,type=int)
        changeCrystal = request.form.get('cc',0,type=int)
        if baseCrystal>oldCrystal+100 or changeCrystal>500000:
            return '{"code":1}'
        newCrystal = baseCrystal+changeCrystal
        userInfoUpdate['crystal'] = newCrystal
    if 'grl' in request.form:
        getRewardList = json.loads(request.form['grl'])
        deleteUserRewards(getRewardList)
    if 'achieves' in request.form:
        achieves = json.loads(request.form['achieves'])
        achieveModule.updateAchieves(uid, achieves)
    if 'research' in request.form:
        researches = json.loads(request.form['research'])
        updateUserResearch(uid, researches)
    if len(deleteBuilds)>0:
        deleteUserBuilds(uid, deleteBuilds)
    if updateBuilds!=None:
        updateUserBuilds(uid, updateBuilds)
    updateUserInfoById(userInfoUpdate, uid)
    updateUserState(uid, int(request.form.get("eid", 0)))
    if 'stat' in request.form:
        statlogger.info("%s\t%d\t%s" % (platform, uid, request.form['stat']))
    if 'bcl' in request.form:
        testlogger.info("[BuyCrystalList]%d\t%s" % (uid, request.form['bcl']))
    if 'adsStatCode' in request.form:
        statlogger.info("%s\t%d\t%s" % (platform, uid, request.form['adsStatCode']))
    loginlogger.info("%s\t%d\tsynData" % (platform,uid))
    return json.dumps({'code':0})

@app.route("/getArenaData2", methods=['GET'])
def getArenaBattle2():
    uid = request.args.get('uid',0,type=int)
    sid = request.args.get('sid',0,type=int)
    atype = request.args.get('atype',0,type=int)
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT aid FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(sid,atype))
    arenaInfo = cur.fetchone()
    if arenaInfo!=None and arenaInfo[0]>0:
        aid = arenaInfo[0]
        cur.execute("SELECT endTime,unum,reward,winner FROM nozomi_arena_battle WHERE id=%s",(aid,))
        data = cur.fetchone()
        ret = dict(endTime=data[0],unum=data[1],reward=data[2],winner=data[3],aid=aid)
        cur.execute("SELECT id,ttype,name FROM nozomi_arena_prepare WHERE aid=%s",(aid,))
        ret['players'] = cur.fetchall()
        cur.execute("SELECT name,ttype,stars,owner,did,res,rid FROM nozomi_arena_town WHERE aid=%s ORDER BY tid ASC",(aid,))
        ret['towns'] = cur.fetchall()
        ret['code'] = 0
        rserver = getRedisServer()
        ugets = rserver.get("uget%d_%d" % (aid,uid))
        if ugets!=None:
            ret['uget'] = json.loads(ugets)
        chance = rserver.get('abnum%d_%d' % (aid,uid))
        if chance==None:
            chance = 5
            rserver.set('abnum%d_%d' % (aid,uid), chance)
        else:
            chance = int(chance)
        ret['chance'] = chance
    else:
        ret = dict(code=1, aid=0, state=0, rewards=getUserRewardsNew(uid))
    return json.dumps(ret)

@app.route("/nextTownData", methods=['POST'])
def nextTownData():
    mdict = request.form
    aid = mdict.get("aid",0,type=int)
    utid = mdict.get("utid",0,type=int)
    tid = mdict.get("tid",0,type=int)
    utype = mdict.get('utype',0,type=int)
    datas = queryAll("SELECT tid,name,ttype,stars,did,res FROM nozomi_arena_town WHERE aid=%s AND tid!=%s AND ttype!=%s AND stars=0",(aid,tid,utype))
    if datas==None:
        return json.dumps(dict(code=0))
    else:
        datas = list(datas)
    random.shuffle(datas)
    ret = dict(code=0)
    max = len(datas)
    rserver = getRedisServer()
    for data in datas:
        tkey = "town%d_%d" % (aid, data[0])
        tvalue = rserver.get(tkey)
        if tvalue!=None and int(tvalue)!=utid:
            continue
        tkey2 = "atkt%d_%d" % (aid, utid)
        tvalue2 = rserver.get(tkey2)
        if tvalue2!=None:
            rserver.delete("town%d_%d" % (aid, int(tvalue2)))
        rserver.setex(tkey2, 360, str(data[0]))
        rserver.setex(tkey, 360, str(utid))
        did = data[4]
        ret['name'] = data[1]
        ret['ttype'] = data[2]
        if utype>0:
            ret['utype'] = utype
        else:
            ret['utype'] = 3-data[2]
        ret['aid'] = aid
        ret['utid'] = utid
        ret['tid'] = data[0]
        ret['stars'] = data[3]
        ret['res'] = data[5]
        if data[2]==0:
            ret['builds'] = json.loads(queryOne("SELECT builds FROM nozomi_town_builds WHERE id=%s",(did,))[0])
        elif did<0:
            ret['builds'] = json.loads(queryOne("SELECT builds FROM nozomi_town_builds WHERE id=%s",(-did,))[0])
        else:
            ret['builds'] = getUserBuilds(did)
    if 'name' not in ret:
        ret['code'] = 1
    return json.dumps(ret)

@app.route("/clearBattleState", methods=['POST'])
def clearBattleState():
    return ""

@app.route("/getTownData", methods=['GET','POST'])
def getTownData():
    mdict = None
    isScout = False
    if request.method=="GET":
        mdict = request.args
        isScout = True
    else:
        mdict = request.form
    aid = mdict.get("aid",0,type=int)
    utid = mdict.get("utid",0,type=int)
    tid = mdict.get("tid",0,type=int)
    data = queryOne("SELECT name,ttype,stars,owner,did,res FROM nozomi_arena_town WHERE aid=%s AND tid=%s",(aid,tid))
    ret = dict(code=0)
    if not isScout:
        rserver = getRedisServer()
        tkey = "town%d_%d" % (aid, tid)
        tvalue = rserver.get(tkey)
        if data[2]==3:
            ret['code'] = 1
            ret['atker'] = data[3]
            ret['star'] = data[2]
        elif tvalue!=None and int(tvalue)!=utid:
            ret['code'] = 2
            ret['atker'] = int(tvalue)
        else:
            tkey2 = "atkt%d_%d" % (aid, utid)
            tvalue2 = rserver.get(tkey2)
            if tvalue2!=None:
                rserver.delete("town%d_%d" % (aid, int(tvalue2)))
            rserver.setex(tkey2, 360, str(tid))
            rserver.setex(tkey, 360, str(utid))
    if ret['code']==0:
        did = data[4]
        ret['name'] = data[0]
        ret['ttype'] = data[1]
        ret['utype'] = 3-data[1]
        ret['aid'] = aid
        ret['utid'] = utid
        ret['tid'] = tid
        ret['stars'] = data[2]
        ret['res'] = data[5]
        if data[1]==0:
            ret['builds'] = json.loads(queryOne("SELECT builds FROM nozomi_town_builds WHERE id=%s",(did,))[0])
        elif did<0:
            ret['builds'] = json.loads(queryOne("SELECT builds FROM nozomi_town_builds WHERE id=%s",(-did,))[0])
        else:
            ret['builds'] = getUserBuilds(did)
    return json.dumps(ret)

@app.route("/buyArena", methods=['POST'])
def buyArena():
    uid = request.form.get("uid",0,type=int)
    bnum = request.form.get("bnum",0,type=int)
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT rewardNums FROM nozomi_user WHERE id=%s",(uid,))
    res = cur.fetchone()
    ret = dict(code=0, bnum=bnum)
    rserver = getRedisServer()
    if bnum==res[0]+1:
        cur.execute("UPDATE nozomi_user SET rewardNums=%s WHERE id=%s", (bnum, uid))
        ccid = rserver.incr("rwdServer")
        crystal = request.form.get("crystal",0,type=int)
        ret['rewards'] = [[ccid,4,0,-crystal,'']]
        cur.execute("INSERT INTO nozomi_reward_new (id,uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s,%s)",(ccid,uid,4,0,-crystal,''))
        con.commit()
    else:
        ret['bnum'] = res[0]
        ccid = rserver.get("rwdServer")
        if ccid!=None:
            ccid = int(ccid)
            cur.execute("SELECT `id`,`type`,`rtype`,`rvalue`,`info` FROM `nozomi_reward_new` WHERE uid=%s AND id<=%s", (uid,ccid))
            rwds = cur.fetchall()
            if rwds!=None:
                ret['rewards'] = rwds
    cur.close()
    return json.dumps(ret)

@app.route("/buyHeroNum", methods=['POST'])
def buyHeroNum():
    uid = request.form.get("uid",0,type=int)
    hnum = request.form.get("hnum",0,type=int)
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT hnum FROM nozomi_user WHERE id=%s",(uid,))
    res = cur.fetchone()
    ret = dict(code=0, hnum=hnum)
    rserver = getRedisServer()
    if hnum==res[0]+1:
        cur.execute("UPDATE nozomi_user SET hnum=%s WHERE id=%s", (hnum, uid))
        ccid = rserver.incr("rwdServer")
        crystal = request.form.get("crystal",0,type=int)
        ret['rewards'] = [[ccid,4,0,-crystal,'']]
        cur.execute("INSERT INTO nozomi_reward_new (id,uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s,%s)",(ccid,uid,4,0,-crystal,''))
        con.commit()
    else:
        ret['hnum'] = res[0]
        ccid = rserver.get("rwdServer")
        if ccid!=None:
            ccid = int(ccid)
            cur.execute("SELECT `id`,`type`,`rtype`,`rvalue`,`info` FROM `nozomi_reward_new` WHERE uid=%s AND id<=%s", (uid,ccid))
            rwds = cur.fetchall()
            if rwds!=None:
                ret['rewards'] = rwds
    cur.close()
    return json.dumps(ret)

@app.route("/prepareTour", methods=['POST'])
def prepareTour():
    uid = request.form.get("uid",0,type=int)
    tid = request.form.get("tid",0,type=int)
    if uid==0 or tid==0:
        return json.dumps(dict(code=1))
    t = int(time.time())
    tour = None
    for stour in stours:
        if stour[0]==tid:
            tour=stour
            break
    if tour==None or tour[4]+tour[7]<=t:
        return json.dumps(dict(code=1))
    update("REPLACE INTO nozomi_user_tour (id,tid,tstage,trank,ttype,star) VALUES (%s,%s,%s,%s,%s,%s)",(uid,tid,0,0,1,0))
    return json.dumps(dict(code=0,tour=[tid,0,0,1,0]))

@app.route("/getTourBattleData", methods=['GET'])
def getTourBattleData():
    uid = request.args.get("uid",0,type=int)
    tid = request.args.get("tid",0,type=int)
    if uid==0 or tid==0:
        return json.dumps(dict(code=1))
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT tid,tstage,trank,ttype,star,tbid FROM nozomi_user_tour WHERE id=%s AND tid=%s",(uid,tid))
    tour = cur.fetchone()
    if tour==None:
        cur.close()
        return json.dumps(dict(code=1))
    cur.execute("SELECT b.id,b.star,u.name,u.level,u.totalCrystal,u.uglevel,b.atk,b.def,b.rid,c.icon,c.name FROM nozomi_tour_battle AS b, nozomi_user AS u LEFT JOIN nozomi_clan AS c ON u.clan=c.id WHERE u.id=b.id AND b.tbid=%s",(tour[5],))
    members = cur.fetchall()
    cur.close()
    return json.dumps(dict(code=0,utour=tour[:5],members=members))

@app.route("/getTourEnemy", methods=['GET'])
def getTourEnemy():
    uid = request.args.get("uid",0,type=int)
    tid = request.args.get("tid",0,type=int)
    eid = request.args.get("eid",0,type=int)
    tstage = request.args.get("tstage",0,type=int)
    if uid==0 or tid==0 or tstage==0 or eid==0:
        return json.dumps(dict(code=1))
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT tbid FROM nozomi_user_tour WHERE id=%s AND tid=%s", (uid,tid))
    tbid = cur.fetchone()
    if tbid==None:
        cur.close()
        return json.dumps(dict(code=1))
    else:
        tbid = tbid[0]
    cur.execute("SELECT id,rid FROM nozomi_tour_battle WHERE tbid=%s AND id=%s",(tbid,eid))
    ebinfo = cur.fetchone()
    ret = dict(code=0)
    if ebinfo==None:
        ret["code"] = 1
    elif ebinfo[1]>0:
        ret["code"] = 2
        ret["subcode"] = 3
    else:
        t = int(time.time())
        tour = None
        for stour in stours:
            if stour[0]==tid:
                tour=stour
                break
        if tour!=None:
            tidx = 5
            if tstage<3:
                tidx = 7+tstage
            if t>tour[4]+tour[tidx]-tour[6]:
                ret["code"] = 2
                ret["subcode"] = 1
        else:
            ret["code"] = 1
    if ret["code"]==0:
        cur.execute("SELECT rid FROM nozomi_tour_cold WHERE tbid=%s AND uid=%s AND eid=%s",(tbid,uid,eid))
        check = cur.fetchone()
        if check!=None:
            ret["code"] = 2
            ret["subcode"] = 4
    if ret["code"]==0:
        rserver = getRedisServer()
        ekey = "tour%d_%d" % (tbid,eid)
        ukey = "attb%d_%d" % (tbid,uid)
        tvalue = rserver.get(ekey)
        if tvalue!=None and int(tvalue)!=uid:
            ret["code"] = 2
            ret["subcode"] = 2
        else:
            tvalue2 = rserver.get(ukey)
            if tvalue2!=None:
                rserver.delete("tour%d_%d" % (tbid, int(tvalue2)))
            rserver.setex(ukey, 360, str(eid))
            rserver.setex(ekey, 360, str(uid))
            ret = getUserInfos(eid)
            ret['code'] = 0
            if ret['clan']>0:
                ret["clanInfo"] = ClanModule.getClanInfo(ret["clan"])
            ret["builds"] = getUserBuilds(eid) 
            ret["userId"] = eid
            ret["tbid"] = tbid
            ret["tid"] = tid
    cur.close()
    return json.dumps(ret)

@app.route("/synTourBattle",methods=["POST"])
def synTourBattle():
    uid = request.form.get("uid",0,type=int)
    tbid = request.form.get("tbid",0,type=int)
    eid = request.form.get("eid",0,type=int)
    stars = request.form.get("stars",0,type=int)
    tid = request.form.get("tid",0,type=int)
    replay = request.form.get("replay")
    if uid==0 or eid==0 or stars<0 or stars>3 or replay==None:
        return json.dumps(dict(code=0))
    con = getConn()
    cur = con.cursor()
    rserver = getRedisServer()
    rserver.delete("attb%d_%d" % (tbid,uid))
    rserver.delete("tour%d_%d" % (tbid,eid))
    addStar = 1
    addUid = eid
    if stars>0:
        addStar = stars*2-1
        addUid = uid
        cur.execute("UPDATE nozomi_tour_battle SET atk=atk+%s,star=star+%s WHERE tbid=%s AND id=%s",(1,addStar,tbid,uid))
        rid = rserver.incr("videoServer")
        cur.execute("INSERT INTO nozomi_replay (id,replay) VALUES (%s,%s)",(rid,replay))
        cur.execute("UPDATE nozomi_tour_battle SET rid=%s WHERE tbid=%s AND id=%s",(rid,tbid,eid))
    else:
        cur.execute("UPDATE nozomi_tour_battle SET def=def+%s,star=star+%s WHERE tbid=%s AND id=%s",(1,1,tbid,eid))
        cur.execute("INSERT IGNORE INTO nozomi_tour_cold (tbid,uid,eid,rid) VALUES (%s,%s,%s,%s)",(tbid,uid,eid,0))
    cur.execute("UPDATE nozomi_user_tour SET star=star+%s WHERE id=%s AND tid=%s",(addStar,addUid,tid))
    rserver.zincrby("utour%d" % tid, addUid, addStar)
    con.commit()
    cur.close()
    return json.dumps(dict(code=0))

ArenaGroups = [[0,5,6,7,8,9,10],[0,27,32,37,50,77,82,87,100]]

@app.route("/prepareArena", methods=['POST'])
def prepareArena():
    uid = request.form.get('uid',0,type=int)
    sid = request.form.get('sid',0,type=int)
    ctime = int(time.time())
    ret = dict(code=0)
    con = getConn()
    cur = con.cursor()
    atype = request.form.get('atype',0,type=int)
    rserver = getRedisServer()
    lkakey = "lock%d_%d" % (sid,atype)
    alock = rserver.incr(lkakey)
    rserver.expire(lkakey,20)
    lktick = 10
    while alock>1 and lktick>0:
        rserver.decr(lkakey)
        print("lock tick", lktick)
        time.sleep(0.5)
        lktick -= 1
        alock = rserver.incr(lkakey)
    if lktick==0:
        print("death alock?")
        rserver.setex(lkakey, 20, 1)
    cur.execute("SELECT aid,btime FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(sid,atype))
    res = cur.fetchone()
    if res!=None:
        if res[0]>0:
            ret['aid'] = res[0]
        ret['atime'] = res[1]
    else:
        tlevel = request.form.get('ulevel',0,type=int)
        eid = 0
        prepareTime = 3600
        battleTime = 43200
        lkkey = "lock"
        tgroup = [0,0]
        tkey = 1
        if atype!=1:
            prepareTime = 1800
            battleTime = 21600
        else:
            tkey = 2
            tlevel = rserver.get("cllv%d" % sid)
            if tlevel==None:
                tlevel = 20
            else:
                tlevel = int(tlevel)
            cur.execute("SELECT members FROM nozomi_clan WHERE id=%s",(sid,))
            mnum = cur.fetchone()
            if mnum!=None:
                mnum = mnum[0]
            else:
                mnum = 10
            if mnum>15:
                tlevel = tlevel/2+50
            else:
                tlevel = tlevel/2
        keygroup = ArenaGroups[tkey-1]
        for tglevel in range(len(keygroup)-1):
            if keygroup[tglevel+1]>=tlevel:
                tgroup[0] = keygroup[tglevel]
                tgroup[1] = keygroup[tglevel+1]
                lkkey = "glock%d_%d" % (tkey, tglevel)
                break
        btime = ctime+prepareTime
        crystal = request.form.get('crystal',0,type=int)
        lktick = 10
        alock = rserver.incr(lkkey)
        while alock>1 and lktick>0:
            rserver.decr(lkkey)
            print("lock tick", lktick)
            time.sleep(0.5)
            lktick -= 1
            alock = rserver.incr(lkkey)
        if lktick>0:
            cutTime = ctime+120
            if tkey==1:
                cur.execute("SELECT id,btime,atype FROM nozomi_arena_prepare WHERE atype>1 AND id!=%s AND ttype>%s AND ttype<=%s AND aid=0 AND btime>%s AND crystal=%s LIMIT 1", (uid,tgroup[0],tgroup[1],cutTime,crystal))
            else:
                cur.execute("SELECT nap.id,nap.btime,nap.atype FROM nozomi_arena_prepare AS nap LEFT JOIN nozomi_clan_cold AS ncc ON ncc.coldKey=nap.id+%s WHERE ncc.coldKey is NULL AND nap.atype=1 AND nap.ttype>%s AND nap.ttype<=%s AND nap.aid=0 AND nap.btime>%s AND nap.crystal=%s LIMIT 1", (sid,tgroup[0],tgroup[1],cutTime,crystal))
            rds = cur.fetchone()
            if rds!=None:
                btime = rds[1]
                eid = rds[0]
                tkey = rds[2]
        else:
            print("death lock?")
            rserver.set(lkkey, 1)
        reward = 0
        if crystal>0:
            reward = crystal+crystal*4/5
            ret['ccid'] = rserver.incr("rwdServer")
            ret['crystal'] = crystal
            cur.execute("INSERT INTO nozomi_reward_new (id,uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s,%s)",(ret['ccid'],uid,0,0,-crystal,''))
        if eid==0:
            cur.execute("INSERT INTO nozomi_arena_prepare (id,atype,state,btime,aid,ttype,name,battlers,rduid,crystal) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sid,atype,1,btime,0,tlevel,'','',uid,crystal))
        else:
            aid = rserver.incr("arenaBattle")
            cur.execute("INSERT INTO nozomi_arena_prepare (id,atype,state,btime,aid,ttype,name,battlers,rduid,crystal) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sid,atype,2,btime,aid,tlevel,'','',uid,crystal))
            cur.execute("UPDATE nozomi_arena_prepare SET state=%s,aid=%s WHERE id=%s AND atype=%s",(2,aid,eid,tkey))
            if atype>2:
                atype = 2
            cur.execute("INSERT INTO nozomi_arena_battle (id,endTime,unum,stage,reward,winner,atype) VALUES (%s,%s,%s,%s,%s,%s,%s)",(aid,btime+battleTime,0,tlevel,reward,0,atype))
            ret['aid'] = aid
        con.commit()
        rserver.decr(lkkey)
        ret['atime'] = btime
    rserver.decr(lkakey)
    cur.close()
    return json.dumps(ret)

@app.route("/getArenaState",methods=['GET'])
def getArenaState():
    sid = request.args.get('sid',0,type=int)
    atype = request.args.get('atype',0,type=int)
    uid = request.args.get("uid",0,type=int)
    r = queryOne("SELECT state,btime,battlers,aid FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(sid,atype))
    ret = dict(code=0,atype=atype)
    if r!=None:
        ret['arena'] = r
    else:
        ret['rewards'] = getUserRewardsNew(uid)
    return json.dumps(ret)

@app.route("/synArenaBattle2",methods=['POST'])
def synArenaBattle2():
    tid = request.form.get('tid', 0, type=int)
    aid = request.form.get('aid', 0, type=int)
    utid = request.form.get('utid', 0, type=int)
    stars = request.form.get('stars',0,type=int)
    atype = request.form.get('atype',0,type=int)
    uid = request.form.get('uid',0,type=int)
    chance = request.form.get("chance",1,type=int)
    if tid==0 or aid==0 or utid==0:
        return json.dumps(dict(code=1))
    rserver = getRedisServer()
    tkey = "town%d_%d" % (aid, tid)
    rserver.delete(tkey)
    rserver.delete("atkt%d_%d" % (aid,utid))
    rnum = rserver.decr("abnum%d_%d" % (aid,uid))
    if rnum<chance-1:
        rserver.incr("abnum%d_%d" % (aid,uid))
        rserver.expire("abnum%d_%d" % (aid,uid), 86400)
        return json.dumps(dict(code=0))
    con = getConn()
    cur = con.cursor()
    if stars>=1:
        rid = 0
        if 'replay' in request.form:
            rid = rserver.incr("videoServer")
            cur.execute("INSERT INTO nozomi_replay (id,replay) VALUES(%s,%s)", (rid,request.form['replay']))
        nuget = json.loads(request.form['uget'])
        if atype==2:
            cur.execute("UPDATE nozomi_arena_town SET res=if(res>%s,res-%s,0) WHERE aid=%s AND tid=%s",(nuget[0],nuget[0],aid,tid))
        cur.execute("UPDATE nozomi_arena_town SET stars=%s,owner=%s,rid=%s WHERE aid=%s AND tid=%s AND stars<%s",(stars,utid,rid,aid,tid,stars))
        con.commit()
        uget = rserver.get("uget%d_%d" % (aid,uid))
        if uget==None:
            rserver.set("uget%d_%d" % (aid,uid), json.dumps(nuget))
        else:
            uget = json.loads(uget)
            rserver.set("uget%d_%d" % (aid,uid), json.dumps([uget[0]+nuget[0],uget[1]+nuget[1],uget[2]+nuget[2],uget[3]+nuget[3]]))
    cur.execute("SELECT reward,unum,winner,atype FROM nozomi_arena_battle WHERE id=%s", (aid, ))
    battle = cur.fetchone()
    if battle==None or battle[2]>0:
        cur.close()
        return json.dumps(dict(code=0))
    arenaChance = rserver.decr("abnum%d" % aid)
    if arenaChance<=0:
        cur.execute("SELECT tid,ttype,owner,stars,did FROM nozomi_arena_town WHERE aid=%s", (aid,))
        ltowns = cur.fetchall()
        tscores = []
        for i in range(battle[1]):
            tscores.append([0,0,[],0,0,0])
        umap = dict()
        for ltown in ltowns:
            ttype = ltown[1]-1
            if ltown[4]>0:
                umap[ltown[0]] = ttype
                tscores[ttype][2].append(ltown[4])
        for ltown in ltowns:
            if ltown[3]>0:
                ttype = umap[ltown[2]]
                tscores[ttype][0] += ltown[3]
        cur.execute("SELECT ttype,id,name,rduid,atype FROM nozomi_arena_prepare WHERE aid=%s",(aid,))
        sinfoRet = cur.fetchall()
        rewardExt = []
        for sinfo in sinfoRet:
            ttype = sinfo[0]-1
            tscores[ttype][3] = sinfo[1]
            tscores[ttype][4] = sinfo[3]
            tscores[ttype][5] = sinfo[4]
            rewardExt.append(sinfo[2])
            rewardExt.append(tscores[ttype][0])
        aresult = 1
        winner = 1
        if tscores[0][0]>tscores[1][0]:
            aresult = 2
        elif tscores[0][0]<tscores[1][0]:
            aresult = 0
            winner = 2
        tscores[0][1] = aresult
        tscores[1][1] = 2-aresult
        arpercents = [20,40,100]
        rewardList = []
        lscoreList = []
        rwdUid = 0
        atypeStr = "Arena"
        if atype==1:
            atypeStr = "LWar"
            rwdUid = tscores[winner-1][4]
            if rwdUid==0:
                rwdUid = int(rserver.get("cleader%d_%d" % (aid,winner)))
        else:
            rwdUid = tscores[winner-1][3]
        for ttype in range(battle[1]):
            ulist = tscores[ttype][2]
            aresult = tscores[ttype][1]
            arenaId = tscores[ttype][5]-1
            apercent = arpercents[aresult]
            totalLS = 0
            for user in ulist:
                rserver.delete("abnum%d_%d" % (aid,user))
                uget = rserver.get("uget%d_%d" % (aid,user))
                if uget==None:
                    uget = [0,0,0,0]
                else:
                    uget = json.loads(uget)
                    rserver.delete("uget%d_%d" % (aid,user))
                reward2 = 0
                if user==rwdUid:
                    reward2 = battle[0]
                ugets = [apercent*uget[0]/100,apercent*uget[1]/100,apercent*uget[2]/100]
                if uget[3]>0:
                    uls = apercent*uget[3]/100
                    lscoreList.append([uls,user])
                    totalLS += uls
                    ugets.append(uget[3]/10)
                rewardList.append([user,3,0,reward2,json.dumps(dict(arena2=atypeStr,aresult=aresult,ai=arenaId,ugets=ugets,ext=rewardExt))])
                if atype==2 and ugets[2]>0:
                    rserver.zincrby("arena", user, ugets[2])
                    rserver.zincrby("arenaRank", user, ugets[2])
            if atype==1:
                rserver.delete("cleader%d_%d" % (aid,ttype+1))
                if totalLS>0:
                    cur.execute("UPDATE nozomi_clan SET score2=score2+%s,score=score+%s WHERE id=%s",(totalLS,totalLS,tscores[ttype][3]))
        cur.execute("UPDATE nozomi_arena_battle SET winner=%s WHERE id=%s",(winner,aid))
        cur.execute("DELETE FROM nozomi_arena_prepare WHERE aid=%s",(aid,))
        cur.executemany("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)",rewardList)
        if atype==1 and len(lscoreList)>0:
            cur.executemany("UPDATE nozomi_user SET lscore=lscore+%s WHERE id=%s",lscoreList)
        if atype==1:
            cur.execute("REPLACE INTO nozomi_clan_cold (coldKey,coldTime) VALUES (%s,%s)",(tscores[0][3]+tscores[1][3],int(time.time())+2*86400))
        con.commit()
        rserver.delete("abnum%d" % aid)
    return json.dumps(dict(code=0))

@app.route("/synStageBattle", methods=['POST'])
def synStageBattle():
    uid = request.form.get("uid",0,type=int)
    sid = request.form.get("sid",0,type=int)
    lres = request.form.get("lres", 0, type=int)
    stars = request.form.get("stars",0,type=int)
    if uid==0 or sid==0 or lres<0 or stars<0 or stars>3:
        return json.dumps(dict(code=1))
    else:
        con = getConn()
        cur = con.cursor()
        cur.execute("SELECT sid FROM nozomi_stages WHERE id=%s ORDER BY sid",(uid,))
        curStages = cur.fetchall()
        if curStages==None:
            curStages = []
        lnum = len(curStages)
        if sid>lnum+1:
            print("fix type 1",uid,sid,stars,lres)
            sid = lnum+1
        lsid = 0
        for nsid in curStages:
            lsid += 1
            if nsid[0]!=lsid:
                print("fix type 2",uid,sid,stars,lres)
                cur.execute("UPDATE nozomi_stages SET sid=%s WHERE id=%s AND sid=%s",(lsid, uid, curStages[lnum-1][0]))
                break
        cur.execute("INSERT INTO nozomi_stages (id,sid,stars,lres) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE stars=if(stars>VALUES(stars),stars,VALUES(stars)), lres=if(lres<VALUES(lres),lres,VALUES(lres))",(uid,sid,stars,lres))
        con.commit()
        cur.close()
        #update("INSERT INTO nozomi_stages (id,sid,stars,lres) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE stars=if(stars>VALUES(stars),stars,VALUES(stars)), lres=if(lres<VALUES(lres),lres,VALUES(lres))",(uid,sid,stars,lres))
        return json.dumps(dict(code=0))

@app.route("/updateLevel", methods=['POST'])
def updateLevel():
    uid = request.form.get("uid",0,type=int)
    level = request.form.get("level",0,type=int)
    if level==2:
        update("INSERT IGNORE INTO nozomi_user_gift2 (id,type,etime,num) VALUE (%s,%s,%s,%s)",(uid,level,int(time.time())+3*86400,20))
    return json.dumps(dict(code=0,ng2=queryAll("SELECT etime,num FROM nozomi_user_gift2 WHERE id=%s",(uid,))))

def isNormal(eid):
    return eid!=1

def updateUserRG(rserver, uid, nscore, cur, ol):
    nl2 = 0
    if nscore>=3200:
        nl2 = 16
    elif nscore>=600:
        nl2 = nscore/200
    elif nscore>=400:
        nl2 = nscore/100-3
    nl = (nl2+2)/3
    if nl2!=ol:
        cur.execute("UPDATE nozomi_user SET uglevel=%s WHERE id=%s",(nl2, uid))
        if ol>0 and nl2!=ol:
            rserver.zrem("urn%d" % ol, uid)
    if nl2>0:
        rserver.zadd("urn%d" % nl2, nscore, uid)
    return nl2

@app.route("/synBattleData", methods=['POST'])
def synBattleData():
    uid = int(request.form.get("uid", 0))
    eid = int(request.form.get("eid", 0))
    incScore = int(request.form.get("score", 0))
    if uid==0 or eid==0:
        abort(401)
    if 'history' in request.form:
        history = json.loads(request.form['history'])
        if history[2]>0 and len(history[7])==0:
            abort(401)
    elif 'isLeague' not in request.form:
        abort(401)
    baseScore = request.form.get("bscore", 0, type=int)
    ebaseScore = request.form.get("ebscore", 0, type=int)
    if incScore>60 or incScore<-60 or (baseScore>ebaseScore and incScore<-30) or (baseScore<ebaseScore and incScore>30):
        testlogger.info("banType 20:%d" % uid)
        abort(401)
    ngrank = 0
    if baseScore>=0 and ebaseScore>=0:
        uinfos = getUserInfos(uid)
        curScore = uinfos['score']
        if curScore!=baseScore:
            return json.dumps(dict(code=1, reason="duplicate request"))
        elif incScore!=0:
            con = getConn()
            cur = con.cursor()
            rserver = getRedisServer()
            baseScore -= incScore
            if baseScore<0:
                baseScore = 0
            ngrank = updateUserRG(rserver, uid, baseScore, cur, uinfos['ug'])
            scores = [[baseScore, uid]]
            rserver.zadd('userRank',baseScore,uid)
            if isNormal(eid):
                einfos = getUserInfos(eid)
                ebaseScore = einfos['score']+incScore
                if ebaseScore<0:
                    ebaseScore = 0
                if einfos['ug']>0:
                    updateUserRG(rserver, eid, ebaseScore, cur, einfos['ug'])
                scores.append([ebaseScore, eid])
                rserver.zadd("userRank",ebaseScore,eid)
            cur.executemany("update nozomi_rank set score=%s where uid=%s", scores)
            cur.executemany("update nozomi_user_state set score=%s where uid=%s", scores)
            cur.executemany("update nozomi_user set score=%s where id=%s", scores)
            con.commit()
            cur.close()
    if isNormal(eid):
        if 'eupdate' in request.form:
            up = json.loads(request.form['eupdate'])
            updateUserBuildExtends(eid, up, request.form.get("fixv",0,type=int))
        if 'hits' in request.form:
            hits = json.loads(request.form['hits'])
            updateUserBuildHitpoints(eid, hits)

        if 'shieldTime' in request.form:
            t = int(request.form['shieldTime'])
            setUserShield(eid, t)
            userInfoUpdate=dict(shieldTime=t)
            updateUserInfoById(userInfoUpdate, eid)
    updateUserState(uid, eid)
    if 'isReverge' in request.form:
        update("UPDATE nozomi_battle_history SET reverged=1 WHERE uid=%s AND eid=%s", (uid, eid))
    if isNormal(eid):
        videoId = 0
        if 'replay' in request.form:
            videoId = insertAndGetId("INSERT INTO nozomi_replay (replay) VALUES(%s)", (request.form['replay']))
        history = json.loads(request.form['history'])
        if len(history)==11:
            udata = getUserInfos(uid)
            history.append(udata['totalCrystal'])
            history.append(udata['level'])
        update("INSERT INTO nozomi_battle_history (uid, eid, videoId, `time`, `info`, reverged) VALUES(%s,%s,%s,%s,%s,0)", (eid, uid, videoId, int(time.mktime(time.localtime())), json.dumps(history)))
    return json.dumps({'code':0,'ng':ngrank})

testUids = [20163, 20157, 20151, 20165, 20159, 20153, 20167, 20161, 20155, 20181, 20175, 20169, 20183, 20177, 20171, 20185, 20179, 20173, 20199, 20193, 20187, 20201, 20195, 20189, 20203, 20197, 20191, 20219, 20213, 20205, 20221, 20215, 20207, 20223, 20217, 20211, 20237, 20231, 20225, 20239, 20233, 20227, 20243, 20235, 20229, 20257, 20251, 20245, 20259, 20253, 20247, 20261, 20255, 20249, 20275, 20269, 20263, 20277, 20271, 20265, 20279, 20273, 20267, 20293, 20287, 20281, 20295, 20289, 20283, 20297, 20291, 20285, 20311, 20305, 20299, 20313, 20307, 20301, 20315, 20309, 20303]
testNames = ['Fiona', 'killer machine', 'Bo Ba La', 'Tough girl', 'Dale_!', 'PrIncE.v', 'Manly killer', 'Caroline', 'Shaun ^_^', 'Aida', 'COOL?LEON', 'Bigbang!', 'BulingBuling', 'Clive', "1t's A Dear", 'Azrael?love', 'Vampire walking', 'Paul.W', 'Louise_smith', 'Evil Man', 'Mr Bean', 'Emily', 'Lonely', 'Moon_Star', 'Devil purify', 'Jeremy1E', 'Penalver', 'Nanncy', 'Crazy baby', 'ONLY love', 'Dreams moment', 'Bergr', 'Fleeting timer', 'Prologue', 'MaTT-', 'DaveR', 'Bob cat', 'Broken wings', 'Kiss or hugs', 'Destiny~', 'Lilia!', 'Dusk Taker', 'Emmanuell', 'Tony Moore', 'Amanda', 'Calvin’S', 'Jack|Rose', '*Madman*', 'Adam?Eve', 'Xerxes', 'Pis over!', 'JenniferCE', 'Walking dead Five', '<LEO>', 'Never say die', 'Tracy', 'One piece!', 'Alexander one', 'Frank rain', 'Silver crow', 'StrawberryM', 'Rik_S', 'LuKas mini', 'King | Club*?*', 'Shine', 'Not a hero', 'Baslilon', 'Smiling at me', 'Provence', 'One More', 'Planet Terror', 'Ben.Lucky', 'Black star', 'Saint Soldier', 'Pretty boy', 'Brandy', 'Temptat10n', 'Storm Wyrm', 'Ace killek', 'Megan Boyle', 'Justin baby']
testLevels = [3,2,4,4,3,4,3,5,5,11,7,11,8,10,10,9,10,11,12,13,15,15,14,18,15,17,18,27,19,20,24,23,26,23,25,28,30,27,39,39,29,26,36,33,44,50,48,49,43,43,35,51,50,52,55,57,70,43,12,45,70,70,63,83,79,64,65,49,65,80,92,86,79,80,65,92,75,64,71,92,97]
testScores = [150,120,100,300,240,200,600,480,400,600,480,400,750,600,500,750,600,500,900,720,600,1050,840,700,1200,960,800,1200,960,800,1350,1080,900,1500,1200,1000,1500,1200,1000,1800,1440,1200,2100,1680,1400,1800,1440,1200,2100,1680,1400,2400,1920,1600,1950,1560,1300,2250,1800,1500,2550,2040,1700,2100,1680,1400,2400,1920,1600,2700,2160,1800,2250,1800,1500,2700,2160,1800,3000,2400,2000]
testPercents = [[25,20],[40,5],[50,5],[15,30],[15,30],[15,30],[5,40],[5,40],[5,35]]
def getTuoUserInfos(tid):
    data = dict(clan=0, mtype=0, totalCrystal=0, userId=1)
    tuoInfo = queryOne("SELECT builds,uinfo FROM nozomi_town_builds WHERE id=%s",(20000+tid,))
    data['builds'] = json.loads(tuoInfo[0])
    uinfo = json.loads(tuoInfo[1])
    data['name'] = uinfo[0]
    data['score'] = uinfo[1]
    data['ug'] = uinfo[2]
    data['level'] = testLevels[tid]
    if data['level']>=70:
        data['totalCrystal'] = 10
    return data

@app.route("/findEnemy", methods=['GET'])
def findEnemy():
    selfUid = int(request.args.get('uid', 0))
    isAdmin = request.args.get('admin')
    uid = 0
    #uid = 37
    tuoid = 0
    r1p = 0
    r2p = 0
    blevel = request.args.get("blevel",0,type=int)
    bscore = request.args.get('baseScore',0,type=int)
    """
    if isAdmin!=None:
        uid = findSpecial(selfUid, blevel)
    else:
        if blevel>=2 and blevel<=10:
            rserver = getRedisServer()
            btnums = rserver.incr("btnum%d" % selfUid)
            if btnums==1:
                rserver.expire("btnum%d" % selfUid, 7200)
            if btnums%4==3 and btnums<72:
                tuoid = (blevel-2)*9+(btnums/4)%9+1
                uid = 1
                r1p = testPercents[(tuoid-1)%9][0]
                r2p = testPercents[(tuoid-1)%9][1]
    """
    if uid==0:
        uid = findAMatch(selfUid, bscore, 200)
    #uid = 29
    if uid==0:
        uid = 1
    data = None
    if uid != 0:
        if tuoid>0:
            data = getTuoUserInfos(tuoid-1)
            data['r1p'] = r1p
            data['r2p'] = r2p
            if data['score']>bscore+10 and bscore>=20:
                data['score'] = bscore+10
        elif uid==1:
            data = dict(clan=0, mtype=0, totalCrystal=0, userId=1)
            if blevel<2:
                blevel = 2
            tid = random.randint((blevel-2)*400+1,(blevel-1)*400)
            townInfo = queryOne("SELECT builds,uinfo FROM nozomi_town_builds WHERE id=%s",(tid,))
            data['builds'] = json.loads(townInfo[0])
            uinfo = json.loads(townInfo[1])
            data['name'] = uinfo[0]
            data['score'] = uinfo[1]
            data['ug'] = uinfo[2]
        else:
            data = getUserInfos(uid)
            if data['clan']>0:
                data['clanInfo'] = ClanModule.getClanInfo(data['clan'])
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

@app.route("/getClanDetails", methods=['GET'])
def getClanDetails():
    cid = int(request.args.get('cid', 0))
    if cid==0:
        return json.dumps(dict(code=1))
    else:
        clanInfo = ClanModule.getClanInfo(cid)
        return json.dumps(dict(code=0, cid=cid, info=clanInfo, members=ClanModule.getClanMembers(cid)))

@app.route("/getLeagueAds", methods=['GET'])
def getLeagueAds():
    t = int(time.time())
    return json.dumps(queryAll("SELECT c.id, c.name, a.text, a.btime, a.etime, c.score2 FROM nozomi_clan as c, nozomi_league_ads as a WHERE a.etime>=%s AND c.id=a.cid AND c.members>0 ORDER BY a.etime ASC LIMIT 5",(t,)))

@app.route("/sendLeagueAd", methods=['POST'])
def sendLeagueAd():
    name = request.form['name']
    uid = request.form.get("uid",0,type=int)
    cid = request.form.get('cid',0,type=int)
    text = request.form['text']
    cost = request.form.get("crystal",0,type=int)
    t = int(time.time())
    ret = dict(code=0)
    con = getConn()
    cur = con.cursor()
    rserver = getRedisServer()
    ccd = rserver.incr("ladCD%d" % cid)
    if ccd==1:
        nt = time.localtime()
        ctime = int(time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 )))+86400
        rserver.expire("ladCD%d" % cid, ctime-t)
        cur.execute("SELECT etime FROM nozomi_league_ads WHERE etime>%s ORDER BY etime DESC LIMIT 5",(t,))
        ets = cur.fetchall()
        if ets!=None and len(ets)==5:
            ret['delay'] = ets[4][0]-t
            t = ets[4][0]
        ccid = rserver.incr("rwdServer")
        cur.execute("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)",(uid,4,0,-cost,''))
        cur.execute("REPLACE INTO nozomi_league_ads (cid,name,text,btime,etime,adnum) VALUES (%s,%s,%s,%s,%s,%s)", (cid,name,text,t,t+3600,0))
        con.commit()
        ret['crystal'] = cost
        ret['ccid'] = ccid
        ret['ad'] = [cid,name,text,t,t+3600]
    else:
        ret["code"] = 1
    cur.close()
    return json.dumps(ret)

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
        return json.dumps(dict(clan=0, info=list(clanInfo), cbe=getClanBoss(user['clan'])))
    else:
        ret = ClanModule.createClan(uid, icon, ltype, name, desc, minScore)
    return json.dumps(dict(clan=ret, info=[ret, icon, 0, ltype, name, desc, 1, minScore, uid, 0, 0], cbe=getClanBoss(ret)))

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
    return json.dumps(dict(code=0, clan=ret[0], clanInfo=ret, cbe=getClanBoss(cid)))

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

@app.route("/modifyClanUser", methods=['POST'])
def modifyClanUser():
    uid = request.form.get('uid',0,type=int)
    tuid = request.form.get('tuid',0,type=int)
    mtype = request.form.get('mtype',0,type=int)
    errorCode = ClanModule.modifyMemberType(uid, tuid, mtype)
    if errorCode==0:
        return json.dumps(dict(code=0))
    else:
        return json.dumps(dict(code=1,subcode=errorCode))

@app.route("/getLeagueRank", methods=['GET'])
def getLeagueRank():
    return json.dumps(ClanModule.getTopClans())

@app.route("/getCaesarsCupRank", methods=['GET'])
def getCaesarsCupRank():
    return json.dumps(ClanModule.getTopClans2())

#client syn the lua error to server
@app.route("/synLuaError", methods=['POST'])
def synLuaError():
    uid = request.form.get('uid', 0, type=int)
    error = request.form.get("error","")
    platform = request.form.get("error","")
    testlogger.info("userId:%d,platform:%s\n%s" % (uid,platform,error))
    return "success"

adminIds = [437,1012,2634]
@app.route("/report", methods=['POST'])
def reportChat():
    uid = request.form.get('uid', 0, type=int)
    eid = request.form.get('eid', 0, type=int)
    msg = request.form.get('msg',"")
    if uid>0 and eid>0 and msg!="":
        if uid in adminIds:
            requestGet("http://10.68.55.40:8005/ban", dict(uid=eid,endtime=int(time.mktime(time.localtime()))+2*86400))
        return "success"
    return "fail"

@app.route("/checkmask", methods=['POST'])
def checkMask():
    uid = request.form.get('uid',0,type=int)
    mask = 1 << (request.form.get('mask',0,type=int))
    umask = getUserMask(uid)
    reward = request.form.get('reward',0,type=int)
    if reward>50:
        reward = 50
    elif reward<5:
        reward = 5
    if (umask&mask)==0:
        update("REPLACE INTO nozomi_user_mask (id,mask) VALUES (%s,%s)", (uid, umask|mask))
        update("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)", (uid,0,0,reward,''))
        return json.dumps(dict(code=0, rewards=getUserRewardsNew(uid)))
    return json.dumps(dict(code=1))

@app.route("/getRewards", methods=['GET'])
def getRewards():
    uid = request.args.get('uid', 0, type=int)
    if uid==0:
        return json.dumps(dict(code=1))
    else:
        l = queryOne("select lastOffTime from nozomi_user where id=%s", (uid,))
        if l==None:
            return json.dumps(dict(code=1))
        return json.dumps(dict(code=0, rewards=getUserRewardsNew(uid), offtime=l[0]))

@app.route("/getMirrorData", methods=['GET'])
def getMirrorData():
    mid = request.args.get('mid', 0, type=int)
    if mid==0:
        return json.dumps(dict(code=1))
    l = queryOne("SELECT mtype,content FROM nozomi_mirrors WHERE id=%s",(mid,))
    if l==None:
        return json.dumps(dict(code=1))
    return json.dumps(dict(code=0,mtype=l[0],content=json.loads(l[1])))

bulletins = ["1. Get free rewards by sharing news with your friends!","2. Download your own particular Battle Video!","3. Continuously login to get more New User Gift!"]

@app.route("/getBulletins", methods=['GET'])
def getButtetins():
    return json.dumps(bulletins)

app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = config.HOSTPORT)
