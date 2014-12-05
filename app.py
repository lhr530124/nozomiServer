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

platformIds = dict(ios=0,android=1,android_mm=2,android_dx=3,android_daqin=4)

dataBuilds = [
              [1, 170018, 1, 1, 0, 1500, "{\"oil\":1000,\"food\":1000}"],
              [2, 110009, 2, 0, 0, 0, ""],
              [3, 130025, 2002, 1, 0, 400, "{\"resource\":500}"],
              [4, 180025, 1000, 1, 0, 400, ""],
              [5, 240023, 2004, 1, 0, 250, "{\"resource\":1}"],
              [6, 350003, 1003, 0, 0, 0, ""],
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
    r = queryOne("SELECT name, score, clan, memberType, level, totalCrystal FROM nozomi_user WHERE id=%s", (uid))
    if r==None:
        return None
    return dict(name=r[0], score=r[1], clan=r[2], mtype=r[3], level=r[4], totalCrystal=r[5])

def getUserMask(uid):
    r = queryOne("SELECT mask FROM nozomi_user_mask WHERE id=%s", (uid,))
    if r==None:
        return 0
    else:
        return r[0]

def getUserAllInfos(uid):
    r = queryOne("SELECT name, score, clan, guideValue, crystal, lastSynTime, shieldTime, zombieTime, obstacleTime, memberType, totalCrystal, lastOffTime, registerTime, ban, rewardNums, magic,level,exp,cmask FROM nozomi_user WHERE id=%s", (uid))
    if r==None:
        return None
    return dict(name=r[0], score=r[1], clan=r[2], guide=r[3], crystal=r[4], lastSynTime=r[5], shieldTime=r[6], zombieTime=r[7], obstacleTime=r[8], mtype=r[9], totalCrystal=r[10], lastOffTime=r[11], registerTime=r[12], ban=r[13], rnum=r[14], mnum=r[15], level=r[16], exp=r[17], cmask=r[18])

def getBindGameCenter(tempName):
    r = queryOne("SELECT gameCenter FROM `nozomi_gc_bind` WHERE uuid=%s",(tempName))
    if r==None:
        return tempName
    else:
        return r[0]

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
    if builds==None or len(builds)==0:
        update("UPDATE nozomi_build SET state=0 WHERE id=%s AND (bid<4000 or bid>=5000)",(uid,),util.getDBID(uid))
        builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM nozomi_build WHERE id=%s AND state=0", (uid), util.getDBID(uid))
    if builds==None or len(builds)==0:
        builds = dataBuilds
        updateUserBuilds(uid, dataBuilds)
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
    if researches==None:
        return [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    return json.loads(researches[0])

def updateUserResearch(uid, researches):
    update("REPLACE INTO nozomi_research (id,research) VALUES (%s,%s)", (uid, json.dumps(researches)))
    
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
    update("UPDATE `nozomi_user` SET crystal=crystal+%s WHERE id=%s", (crystal, uid))

def checkUserReward(uid, ln=0):
    remark = "remark"
    if ln==1:
        remark = "remark_cn"
    allRewards = queryAll("SELECT reward, "+remark+" FROM `nozomi_reward` WHERE uid=%s", (uid))
    if allRewards!=None and len(allRewards)>0:
        sumReward = 0
        for rewardItem in allRewards:
            sumReward = sumReward+rewardItem[0]
        updateCrystal(uid, sumReward)
        update("DELETE FROM `nozomi_reward` WHERE uid=%s",(uid))
        return [sumReward, allRewards]
    else:
        return None

def addOurAds(uid, platform, data):
    curTime = data["serverTime"]
    if platform=="android_our":
        adsCode = 1
        adsUrl = "https://play.google.com/store/apps/details?id=com.caesars.flyGame"
        if curTime<1392940800:
            needAds = False
            ret = queryOne("SELECT code, lastTime FROM nozomi_ads_check WHERE id=%s", (uid))
            if ret==None:
                needAds = True
                update("INSERT INTO nozomi_ads_check (id,code,lastTime) VALUES (%s,%s,%s)", (uid, adsCode, curTime))
            elif ret[0]!=adsCode or ret[1]<curTime-86400:
                needAds = True
                update("UPDATE nozomi_ads_check SET code=%s, lastTime=%s WHERE id=%s", (adsCode,curTime,uid))
            if needAds:
                data['adsCode'] = adsCode
                data['adsUrl'] = adsUrl

dailyGiftReward = [[1,1000],[1,1500],[0,10],[1,2000],[1,2500],[1,3000],[0,50],[1,3500],[1,4000],[1,4500],[1,5000],[1,6500],[1,7000],[1,8000],[0,100],[1,9000],[1,10000],[1,11000],[1,12000],[1,13000],[1,14000],[1,15000],[1,17000],[1,19000],[1,21000],[1,23000],[1,25000],[1,27000],[1,30000],[0,500]]
def newUserLogin(uid):
    today = datetime.date.today()
    ret = queryOne("SELECT regDate,loginDate,loginDays,maxLDays,curLDays,lottery,lotterySeed FROM `nozomi_login_new` WHERE `id`=%s", (uid))
    newGift = 0
    newLogin = False
    loginDays = 1
    curLDays = 1
    lt = 0
    lts = random.randint(10000,20000)
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
            update("UPDATE `nozomi_login_new` SET loginDate=%s,loginDays=%s,maxLDays=%s,curLDays=%s,lottery=0,lotterySeed=%s WHERE `id`=%s",(today,loginDays,maxLDays,curLDays,lts,uid))
        else:
            loginDays = ret[2]
            curLDays = ret[4]
            lt = ret[5]
            lts = ret[6]
    else:
        newGift = 1
        newLogin = True
        update("INSERT INTO `nozomi_login_new` (`id`,regDate,loginDate,loginDays,maxLDays,curLDays,lottery,lotterySeed) VALUES(%s,%s,%s,1,1,1,0,%s)", (uid, today, today, lts))
    if newGift>0:
        reward = dailyGiftReward[(newGift-1)%30]
        update("DELETE FROM `nozomi_reward_new` WHERE uid=%s AND `type`=%s", (uid,1))
        update("INSERT INTO `nozomi_reward_new` (uid,`type`,`rtype`,`rvalue`,`info`) VALUES(%s,%s,%s,%s,%s)", (uid,1,reward[0],reward[1],json.dumps(dict(day=newGift))))
    return [0, loginDays, curLDays, newLogin, lt, lts]

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

def initUser(username, nickname, platform):
    print "initUser", username, nickname
    regTime = int(time.mktime(time.localtime()))
    platformId = platformIds.get(platform, 0)
    initScore = 0
    initCrystal = 500
    #uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, registerTime, score, crystal, shieldTime, platform) VALUES(%s, %s, %s, %s, 500, 497, 0, %s)", (username, regTime, nickname, util.getTime(), platformId))
    uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, registerTime, score, crystal, shieldTime, platform, lastOffTime, magic, level) VALUES(%s, %s, %s, %s, 0, %s, 0, %s, %s, 0, 1)", (username, regTime, "", util.getTime(), initCrystal, platformId, regTime))

    module.UserRankModule.initUserScore(uid, initScore)

    updateUserBuilds(uid, dataBuilds)
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
        try:
            return json.dumps([[json.loads(r[0]), r[1], r[2], r[3], r[4]] for r in ret])
        except Exception as e:
            app.logger.exception('''
            url %s
            args %s
            form %s
            ''' % (request.url, str(request.args), str(request.form)))
            return "[]"

@app.route("/login", methods=['POST', 'GET'])
def login():
    tempname = None
    if 'tempname' in request.form:
        tempname = request.form['tempname']
    username = None
    if 'username' in request.form:
        username = request.form['username']
    servertest = False
    plat = "ios"
    if 'platform' in request.form:
        plat = request.form['platform']
    if 'admin' in request.form:
        uinfos = queryAll("SELECT t.id, u.name FROM nozomi_test_users as t, nozomi_user as u where t.id=u.id and t.state=0 order by t.id")
        ret = dict(code=0, uinfos=uinfos)
        return json.dumps(ret)
    if tempname!=None:
        if username==None:
            username = getBindGameCenter(tempname)
        else:
            bindGameCenter(username, tempname)
    if username!=None:
        uid = getUidByName(username)
        ret = dict(code=0, uid=uid)
        if uid==0:
            timelogger.info("new user %s %d " % (username, uid))
            uid = initUser(username, '', plat)
            loginlogger.info("%s\t%d\treg" % (plat,uid))
            achieveModule.initAchieves(uid)
            ret['uid'] = uid
        return json.dumps(ret)
    else:
        #time.sleep(209) 
        return "{'code':401}"
        #测试timeout
        #pass

updateUrls = dict()
settings = [15,int(time.mktime((2014,9,1,12,0,0,0,0,0)))-util.beginTime, True, int(time.mktime((2013,11,26,6,0,0,0,0,0)))-util.beginTime,15]
newActivitys = [[1416614400,1416787200,"act1",0,8,2419200],[1417219200,1417305600,"act2",30,16,2419200],[1417824000,1417910400,"act3",30,32,2419200],[1418428800,1418515200,"act4",30,64,2419200],[1417824000,1417996800,"act6",20,256,0]]
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
            if checkVersion>settings[0] and request.args.get("cc")!="com.caesars.zclash":
                shouldDebug = True
        data = getUserAllInfos(uid)
        if data==None or data['ban']!=0:
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
        state = getUserState(uid)
        if 'attackTime' in state:
            return json.dumps(state)
        if data['cmask']>0:
            ret = dict(serverUpdate=1)
            forceUpdate = False
            if cc.find("com.caesars.empire")==0:
                ret['url'] = "https://itunes.apple.com/app/id915963054?mt=8&uo=4"
                forceUpdate = True
            elif cc.find("com.caesars.nozomi")==0:
                ret['url'] = "https://play.google.com/store/apps/details?id=com.caesars.zclash"
                forceUpdate = True
            elif data['cmask']>1:
                update("UPDATE nozomi_user SET cmask=1 WHERE id=%s",(uid,))
                info = dict(nos=1)
                if lang=="CN":
                    info['title'] = "感谢你的更新！"
                    info['text'] = "感谢你更新了新版本！我们给予了你100水晶作为奖励！"
                elif lang=="HK":
                    info['title'] = "感謝你的更新！"
                    info['text'] = "感謝你更新了新版本！我們給予了你100水晶作爲獎勵！"
                else:
                    info['title'] = "Thanks for update!"
                    info['text'] = "Thanks for update our new version! We send you 100 crystals as reward!"
                update("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)",(uid,3,0,100,json.dumps(info)))
            if forceUpdate:
                ret['forceUpdate'] = 1
                ret['button2'] = ""
                ret['cmask'] = cmask
                if lang=="CN":
                    ret['title'] = "请更新版本！"
                    ret['content'] = "十分抱歉，由于服务器原因，需要您下载版本。您的数据将不会改变，进入新版本后您将获得100水晶补偿。"
                    ret['button1'] = "下载"
                elif lang=="HK":
                    ret['title'] = "請更新版本！"
                    ret['content'] = "十分抱歉，由于服務器原因，需要您下載版本。您的數據將不會改變，進入新版本後您將獲得100水晶補償。"
                    ret['button1'] = "下載"
                else:
                    ret['title'] = "Update New Version!"
                    ret['content'] = "Sorry, you need download a new version because of server's problem. Your data won't be changed and you will get 100 Crystals as compensation."
                    ret['button1'] = "Download"
                return json.dumps(ret)
        if ret!=None:
            data.update(ret)
        t = int(time.mktime(time.localtime()))
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
        data['newRewards'] = getUserRewardsNew(uid)
        data['mask'] = getUserMask(uid)
        zdc = queryOne("SELECT chance,stage,etime FROM nozomi_zombie_challenge WHERE id=%s",(uid,))
        if zdc!=None:
            data['zdc'] = zdc
        stages = queryAll("SELECT stars,lres FROM nozomi_stages WHERE id=%s ORDER BY sid",(uid,))
        if stages!=None:
            data['stages'] = stages
        for nact in newActivitys:
            while nact[1]<t and nact[5]>0:
                nact[0] += nact[5]
                nact[1] += nact[5]
        data['nacts'] = newActivitys
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
        arena = queryOne("SELECT state,btime FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(uid,2))
        if arena!=None:
            data['arena2'] = arena
        if data['guide']>=1400:
            data['ng2'] = queryAll("SELECT etime,num FROM nozomi_user_gift2 WHERE id=%s",(uid,))
        rserver = getRedisServer()
        rid = random.randint(0, 1000000) 
        ug = rserver.hget("ugrank", uid)
        if ug==None:
            ug = 0
        else:
            ug = int(ug)
        data['ug'] = ug
        data['treq'] = rid
        rserver.set("utoken%d" % uid, rid)
        rserver.expire("utoken%d" % uid, 3600)
        loginlogger.info("%s\t%d\tlogin\t%d" % (platform,uid,rid))
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
            updateUserBuildExtends(uid, repairDatas)
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
                elif build[2]<7000 and build[3]>oldBuild[3] and build[2]!=3006:
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
        update("UPDATE nozomi_build SET extend=%s WHERE id=%s AND bid=1000",('{"soldiers":[0,0,0,0,0,0,0,0,0,0,0,0]}',uid),util.getDBID(uid))
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
            if nrid>rid or nrid<rid-1:
                print("token error, may be login in two device", uid)
                return json.dumps({'code':2,'subcode':1})
            elif nrid==rid-1:
                print("token the same, may be syn data twice", uid)
                return json.dumps(dict(code=0,subcode=0))
            else:
                rid += 1
                rserver.set("utoken%d" % uid, rid)
                rserver.expire("utoken%d" % uid, 7200)
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
        updateBuilds = json.loads(updateBuilds)
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
        if baseCrystal>oldCrystal+100 or changeCrystal>100000:
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
        cur.execute("SELECT name,ttype,stars,owner,did,res FROM nozomi_arena_town WHERE aid=%s ORDER BY tid ASC",(aid,))
        ret['towns'] = cur.fetchall()
        ret['code'] = 0
        rserver = getRedisServer()
        ugets = rserver.get("uget%d_%d" % (aid,uid))
        if ugets!=None:
            ret['uget'] = json.loads(ugets)
        chance = rserver.get('abnum%d_%d' % (aid,uid))
        if chance==None:
            chance = 5
            if atype==1:
                chance = 2
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
        rserver.set(tkey2, str(data[0]))
        rserver.expire(tkey2, 360)
        rserver.set(tkey, str(utid))
        rserver.expire(tkey, 360)
        did = data[4]
        ret['name'] = data[1]
        ret['ttype'] = data[2]
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
    if data[2]>0:
        ret['code'] = 1
        ret['atker'] = data[3]
        ret['star'] = data[2]
    else:
        if not isScout:
            rserver = getRedisServer()
            tkey = "town%d_%d" % (aid, tid)
            tvalue = rserver.get(tkey)
            if tvalue!=None and int(tvalue)!=utid:
                ret['code'] = 2
                ret['atker'] = int(tvalue)
            else:
                tkey2 = "atkt%d_%d" % (aid, utid)
                tvalue2 = rserver.get(tkey2)
                if tvalue2!=None:
                    rserver.delete("town%d_%d" % (aid, int(tvalue2)))
                rserver.set(tkey2, str(tid))
                rserver.expire(tkey2, 360)
                rserver.set(tkey, str(utid))
                rserver.expire(tkey, 360)
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
        rserver.set(ldakey, 1)
        rserver.expire(ldakey, 20)
    cur.execute("SELECT aid,btime FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(sid,atype))
    res = cur.fetchone()
    if res!=None:
        if res[0]>0:
            ret['aid'] = res[0]
        ret['atime'] = res[1]
    else:
        eid = 0
        prepareTime = 3600
        #if atype==1:
        #    prepareTime = 86400
        btime = ctime+prepareTime
        tlevel = request.form.get('ulevel',0,type=int)
        crystal = request.form.get('crystal',0,type=int)
        lkkey = "lock%d_%d_%d" % (atype,tlevel,crystal)
        rdkey = "ready%d_%d_%d" % (atype,tlevel,crystal)
        lktick = 10
        alock = rserver.incr(lkkey)
        while alock>1 and lktick>0:
            rserver.decr(lkkey)
            print("lock tick", lktick)
            time.sleep(0.5)
            lktick -= 1
            alock = rserver.incr(lkkey)
        if lktick>0:
            readyed = rserver.get(rdkey)
            if readyed!=None:
                rserver.delete(rdkey)
                rds = readyed.split("_")
                btime = int(rds[1])
                if btime<ctime+60:
                    btime = ctime+prepareTime
                else:
                    eid = int(rds[0])
        else:
            print("death lock?")
            rserver.set(lkkey, 1)
        if eid==0:
            rserver.set(rdkey, "%d_%d" % (sid, btime))
            rserver.expire(rdkey, prepareTime-3*60)
        rserver.decr(lkkey)
        reward = 0
        if crystal>0:
            reward = crystal+crystal*4/5
            ret['ccid'] = rserver.incr("rwdServer")
            ret['crystal'] = crystal
            cur.execute("INSERT INTO nozomi_reward_new (id,uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s,%s)",(ret['ccid'],uid,0,0,-crystal,''))
        if eid==0:
            cur.execute("INSERT INTO nozomi_arena_prepare (id,atype,state,btime,aid,ttype,name,battlers,rduid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sid,atype,1,btime,0,0,'','',uid))
            rserver.set("pcost%d_%d" % (atype,sid), "%d_%d" % (uid,crystal))
        else:
            rserver.delete("pcost%d_%d" % (atype,eid))
            aid = rserver.incr("arenaBattle")
            cur.execute("INSERT INTO nozomi_arena_prepare (id,atype,state,btime,aid,ttype,name,battlers,rduid) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",(sid,atype,2,btime,aid,0,'','',uid))
            cur.execute("UPDATE nozomi_arena_prepare SET state=%s,aid=%s WHERE id=%s AND atype=%s",(2,aid,eid,atype))
            cur.execute("INSERT INTO nozomi_arena_battle (id,endTime,unum,stage,reward,winner,atype) VALUES (%s,%s,%s,%s,%s,%s,%s)",(aid,btime+86400,0,tlevel,reward,0,atype))
            ret['aid'] = aid
        con.commit()
        ret['atime'] = btime
    rserver.decr(lkakey)
    cur.close()
    return json.dumps(ret)

@app.route("/getArenaState",methods=['GET'])
def getArenaState():
    sid = request.args.get('sid',0,type=int)
    atype = request.args.get('atype',0,type=int)
    r = queryOne("SELECT state,btime,battlers,aid FROM nozomi_arena_prepare WHERE id=%s AND atype=%s",(sid,atype))
    ret = dict(code=0,atype=atype)
    if r!=None:
        ret['arena'] = r
    return json.dumps(ret)

@app.route("/synArenaBattle2",methods=['POST'])
def synArenaBattle2():
    tid = request.form.get('tid', 0, type=int)
    aid = request.form.get('aid', 0, type=int)
    utid = request.form.get('utid', 0, type=int)
    stars = request.form.get('stars',0,type=int)
    atype = request.form.get('atype',0,type=int)
    uid = request.form.get('uid',0,type=int)
    if tid==0 or aid==0 or utid==0:
        return json.dumps(dict(code=1))
    rserver = getRedisServer()
    tkey = "town%d_%d" % (aid, tid)
    rserver.delete(tkey)
    rserver.delete("atkt%d_%d" % (aid,utid))
    rnum = rserver.decr("abnum%d_%d" % (aid,uid))
    if rnum<0:
        rserver.incr("abnum%d_%d" % (aid,uid))
        rserver.expire("abnum%d_%d" % (aid,uid), 86400)
        return json.dumps(dict(code=0))
    con = getConn()
    cur = con.cursor()
    if stars>=1:
        cur.execute("UPDATE nozomi_arena_town SET stars=%s,owner=%s WHERE aid=%s AND tid=%s AND stars<%s",(stars,utid,aid,tid,stars))
        con.commit()
        uget = rserver.get("uget%d_%d" % (aid,uid))
        nuget = request.form['uget']
        if uget==None:
            rserver.set("uget%d_%d" % (aid,uid), nuget)
        else:
            nuget = json.loads(nuget)
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
            tscores.append([0,0,[],0,0])
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
        cur.execute("SELECT ttype,id,name,rduid FROM nozomi_arena_prepare WHERE aid=%s",(aid,))
        sinfoRet = cur.fetchall()
        rewardExt = []
        for sinfo in sinfoRet:
            ttype = sinfo[0]-1
            tscores[ttype][3] = sinfo[1]
            tscores[ttype][4] = sinfo[3]
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
                rewardList.append([user,3,0,reward2,json.dumps(dict(arena2=atypeStr,aresult=aresult,ugets=ugets,ext=rewardExt))])
                if atype==2 and ugets[2]>0:
                    UserRankModule.updateRankNormal(user,"arena",ugets[2])
                    UserRankModule.updateRankNormal(user,"arenaRank",ugets[2])
            if atype==1:
                rserver.delete("cleader%d_%d" % (aid,ttype+1))
                if totalLS>0:
                    cur.execute("UPDATE nozomi_clan SET score2=score2+%s,score=score+%s WHERE id=%s",(totalLS,totalLS,tscores[ttype][3]))
        cur.execute("UPDATE nozomi_arena_battle SET winner=%s WHERE id=%s",(winner,aid))
        cur.execute("DELETE FROM nozomi_arena_prepare WHERE aid=%s",(aid,))
        cur.executemany("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)",rewardList)
        if atype==1 and len(lscoreList)>0:
            cur.executemany("UPDATE nozomi_user SET lscore=lscore+%s WHERE id=%s",lscoreList)
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
        update("INSERT INTO nozomi_stages (id,sid,stars,lres) VALUES (%s,%s,%s,%s) ON DUPLICATE KEY UPDATE stars=if(stars>VALUES(stars),stars,VALUES(stars)), lres=if(lres<VALUES(lres),lres,VALUES(lres))",(uid,sid,stars,lres))
        return json.dumps(dict(code=0))

@app.route("/updateLevel", methods=['POST'])
def updateLevel():
    uid = request.form.get("uid",0,type=int)
    level = request.form.get("level",0,type=int)
    if level==2 or level==5:
        update("INSERT IGNORE INTO nozomi_user_gift2 (id,type,etime,num) VALUE (%s,%s,%s,%s)",(uid,level,int(time.time())+3*86400,20))
    return json.dumps(dict(code=0,ng2=queryAll("SELECT etime,num FROM nozomi_user_gift2 WHERE id=%s",(uid,))))

def isNormal(eid):
    if eid==1 or (eid>=20151 and eid<=20315 and eid!=20182 and eid!=20224 and eid!=20241 and eid!=20284):
        return False
    return True

def updateUserRG(rserver, uid, nscore):
    ol = rserver.hget("ugrank", uid)
    if ol==None:
        ol = 0
    else:
        ol = int(ol)
    nl2 = 0
    if nscore>=3200:
        nl2 = 16
    elif nscore>=600:
        nl2 = nscore/200
    elif nscore>=400:
        nl2 = nscore/100-3
    nl = (nl2+2)/3
    if nl2!=ol:
        rserver.hset("ugrank", uid, nl2)
        ol = (ol+2)/3
        if ol>0 and nl!=ol:
            rserver.zrem("ur%d" % ol, uid)
    if nl>0:
        rserver.zadd("ur%d" % nl, nscore, uid)
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
    ngrank = 0
    if baseScore>=0 and ebaseScore>=0:
        curScore = getUserInfos(uid)['score']
        if curScore!=baseScore:
            return json.dumps(dict(code=1, reason="duplicate request"))
        elif incScore!=0:
            rserver = getRedisServer()
            baseScore -= incScore
            ngrank = updateUserRG(rserver, uid, baseScore)
            scores = [[baseScore, uid]]
            rserver.zadd('userRank',baseScore,uid)
            if isNormal(eid):
                ebaseScore += incScore
                scores.append([ebaseScore, eid])
                rserver.zadd("userRank",ebaseScore,eid)
            con = getConn()
            cur = con.cursor()
            cur.executemany("update nozomi_rank set score=%s where uid=%s", scores)
            cur.executemany("update nozomi_user_state set score=%s where uid=%s", scores)
            cur.executemany("update nozomi_user set score=%s where id=%s", scores)
            con.commit()
            cur.close()
    if isNormal(eid):
        if 'eupdate' in request.form:
            up = json.loads(request.form['eupdate'])
            updateUserBuildExtends(eid, up)
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
    if isAdmin!=None:
        uid = findSpecial(selfUid, blevel)
    else:
        if blevel>=2 and blevel<=10:
            rserver = getRedisServer()
            btnums = rserver.incr("btnum%d" % selfUid)
            if btnums==1:
                rserver.expire("btnum%d" % selfUid, 7200)
            if btnums%2==1 and btnums<19:
                tuoid = (blevel-2)*9+(btnums/2)%9+1
                uid = testUids[tuoid-1]
                if tuoid%3==1:
                    r1p = 70
                    r2p = 10
                elif tuoid%3==2:
                    r1p = 40
                    r2p = 40
                else:
                    r1p = 10
                    r2p = 70
    if uid==0:
        uid = findAMatch(selfUid, int(request.args.get('baseScore', 0)), 200)
    #uid = 29
    if uid==0:
        uid = 1
    if uid != 0:
        data = getUserInfos(uid)
        if data['clan']>0:
            data['clanInfo'] = ClanModule.getClanInfo(data['clan'])
        data['builds'] = getUserBuilds(uid)
        data['userId'] = uid
        if tuoid>0:
            data['r1p'] = r1p
            data['r2p'] = r2p
            data['name'] = testNames[tuoid-1]
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
