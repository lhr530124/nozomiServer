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
from hashlib import md5
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
import IpSocketHandler

from MySQLdb import cursors, connections
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
    
    
#可能没有web 上下文环境
def getConn():
    return MySQLdb.connect(host=app.config['HOST'], user=app.config['USER'], passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')


def getMyConn():
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = MySQLdb.connect(host=app.config['HOST'], user=app.config['USER'], passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')
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

newbieCup = [int(time.mktime((2013,6,31,0,0,0,0,0,0)))-util.beginTime, int(time.mktime((2013,9,10,0,0,0,0,0,0)))]

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
    r = queryOne("SELECT name, score, clan, guideValue, crystal, lastSynTime, shieldTime, zombieTime, obstacleTime, memberType, totalCrystal, lastOffTime, registerTime FROM nozomi_user WHERE id=%s", (uid))
    return dict(name=r[0], score=r[1], clan=r[2], guide=r[3], crystal=r[4], lastSynTime=r[5], shieldTime=r[6], zombieTime=r[7], obstacleTime=r[8], mtype=r[9], totalCrystal=r[10], lastOffTime=r[11], registerTime=r[12])

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
    util.restoreBuilds(uid)
    builds = queryAll("SELECT buildIndex, grid, bid, level, time, hitpoints, extend FROM nozomi_build WHERE id=%s AND state=0", (uid), util.getDBID(uid))
    return builds

def deleteUserBuilds(uid, buildIndexes):
    params = []
    for bindex in buildIndexes:
        params.append([uid, bindex])
    util.restoreBuilds(uid)
    executemany("UPDATE nozomi_build SET state=1 WHERE id=%s AND buildIndex=%s", params, dbID=util.getDBID(uid))

def updateUserBuilds(uid, datas):
    params = []
    for data in datas:
        params.append([uid, data[0], data[1], data[2], data[3], data[4], data[5], data[6]])
    util.restoreBuilds(uid)
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
    util.restoreBuilds(uid)
    executemany("UPDATE nozomi_build SET hitpoints=%s WHERE id=%s AND buildIndex=%s", params, util.getDBID(uid))

def updateUserBuildExtends(uid, datas):
    params = []
    for data in datas:
        params.append([data[1], uid, data[0]])
    util.restoreBuilds(uid)
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

def newUserLogin(uid):
    today = datetime.date.today()
    ret = queryOne("SELECT regDate,loginDate,loginDays,maxLDays,curLDays FROM `nozomi_login_new` WHERE `id`=%s", (uid))
    leftDay = 10
    newGift = 0
    if ret!=None:
        timedelta = (today-ret[0]).days
        if timedelta>10:
            leftDay = 0
        elif ret[2]<7:
            leftDay = 7-ret[2]
        else:
            leftDay = 1
        timedelta = (today-ret[1]).days
        if timedelta>0:
            loginDays = ret[2]+1
            if loginDays<7:
                newGift = loginDays
            curLDays = 1
            maxLDays = ret[3]
            if timedelta==1:
                curLDays = ret[4]+1
                if curLDays>maxLDays:
                    maxLDays = curLDays
            update("UPDATE `nozomi_login_new` SET loginDate=%s,loginDays=%s,maxLDays=%s,curLDays=%s WHERE `id`=%s",(today,loginDays,maxLDays,curLDays,uid))
    else:
        newGift = 1
        update("INSERT INTO `nozomi_login_new` (`id`,regDate,loginDate,loginDays,maxLDays,curLDays) VALUES(%s,%s,%s,1,1,1)", (uid, today, today))
    if newGift>0:
        reward = [[1,800],[1,1500],[0,50],[1,3000],[1,5000],[0,100]][newGift-1]
        update("INSERT INTO `nozomi_reward_new` (uid,`type`,`rtype`,`rvalue`,`info`) VALUES(%s,%s,%s,%s,%s)", (uid,1,reward[0],reward[1],json.dumps(dict(day=newGift))))
    return leftDay

def getUserRewardsNew(uid):
    allRewards = queryAll("SELECT `id`,`type`,`rtype`,`rvalue`,`info` FROM `nozomi_reward_new` WHERE uid=%s", (uid))
    if allRewards!=None and len(allRewards)>0:
        return allRewards
    else:
        return []

def deleteUserRewards(rwList):
    executemany("DELETE FROM `nozomi_reward_new` WHERE id=%s", rwList)

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
    initScore = 500
    #uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, registerTime, score, crystal, shieldTime, platform) VALUES(%s, %s, %s, %s, 500, 497, 0, %s)", (username, regTime, nickname, util.getTime(), platformId))
    uid = insertAndGetId("INSERT INTO nozomi_user (account, lastSynTime, name, registerTime, score, crystal, shieldTime, platform, lastOffTime) VALUES(%s, %s, %s, %s, 500, 497, 0, %s, %s)", (username, regTime, nickname, util.getTime(), platformId, regTime))

    myCon = getConn()
    module.UserRankModule.initUserScore(myCon, uid, initScore)
    module.UserRankModule.updateScore(myCon, uid, initScore)
    myCon.commit()
    myCon.close()

    updateUserBuilds(uid, dataBuilds)
    update("INSERT INTO nozomi_research (id, research) VALUES(%s, '[1, 1, 1, 1, 1, 1, 1, 1, 1, 1]')", (uid))
    newUserState(uid)
    
    return uid

def getTopNewbies():
    return queryAll("SELECT ns.id,ns.score,ns.name,nc.icon,nc.name FROM `nozomi_user` AS ns LEFT JOIN `nozomi_clan` AS nc ON ns.clan=nc.id WHERE ns.registerTime>%s ORDER BY score DESC LIMIT 100",(newbieCup[0]))

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
    print 'login', request.form
    tempname = None
    if 'tempname' in request.form:
        tempname = request.form['tempname']
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
            timelogger.info("new user %s %d " % (username, uid))
            print "new user"
            nickname = request.form['nickname']
            platform = "ios"
            if 'platform' in request.form:
                platform = request.form['platform']
            uid = initUser(username, nickname, platform)
            loginlogger.info("%s\t%d\treg" % (platform,uid))
            achieveModule.initAchieves(uid)
            ret['uid'] = uid
        else:
            ban = queryOne('select ban from nozomi_user where id = %s', (uid))[0]
            if ban != 0:
                abort(401)

        return json.dumps(ret)
    else:
        #time.sleep(209) 
        return "{'code':401}"
        #测试timeout
        #pass

updateUrls = dict()
settings = [5,int(time.mktime((2013,9,22,2,0,0,0,0,0)))-util.beginTime, False, int(time.mktime((2013,11,26,6,0,0,0,0,0)))-util.beginTime]

@app.route("/getData", methods=['GET'])
def getData():
    print 'getData', request.args
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
        ret = None
        """
        if 'check' in request.args:
            checkVersion = request.args.get("checkVersion", 0, type=int)
            if checkVersion<settings[0] and language==0:
                country = request.args.get('country',"us").lower()
                ret = dict(serverUpdate=1)
                if language==0:
                    ret['title'] = "Version 3.2"
                    ret['content']="1. Some Bugs fixed\n- Fix connection error bug;\n- Fix chat room related bug;\n\n2. Functions Optimized\n- Add First Recharge Rewards;\n- Add New Users Gift;\n- Perfect Zombie Attack Function;\n- Perfect New user guide;\n- Add share rewards;\n\n3. Coming soon in the next version\n- Hero system;\n- You can also give us your ideas by email"
                    ret['button1']="Update Now"
                    ret['button2']="Later"
                else:
                    ret['title'] = "3.1版本"
                    ret['content'] = "1. 上线导弹工厂，可以建造超级武器啦！\n2. 上线了踢出功能，盟主可以踢出成员啦！\n3. 上线了分享奖励免费水晶功能！\n4. 修复了若干bug。"
                    ret['button1']="立即更新"
                    ret['button2']="稍后更新"
                if country in updateUrls:
                    ret['url'] = updateUrls[country]
                else:
                    url = queryOne("SELECT url FROM nozomi_ios_update_url WHERE country=%s",(country))
                    if url!=None:
                        updateUrls[country] = url[0]
                        ret['url'] = url[0]
                    elif 'us' in updateUrls:
                        ret['url'] = updateUrls['us']
                    else:
                        url = queryOne("SELECT url FROM nozomi_ios_update_url WHERE country='us'")[0]
                        updateUrls['us'] = url
                        ret['url'] = url
                #if platform=="ios_cn":
                #    ret['url'] = ret['url'].replace("608847384","666289981")
                if settings[2]==True:
                    ret['forceUpdate']=1
                    return json.dumps(ret)
        """
        state = getUserState(uid)
        if 'attackTime' in state:
            return json.dumps(state)
        data = getUserAllInfos(uid)
        if ret!=None:
            data.update(ret)
        t = int(time.mktime(time.localtime()))
        data['serverTime'] = t
        #while t>util.leagueWarStartTime:
        #    util.leagueWarStartTime = util.leagueWarStartTime+86400*14
        #while t>util.leagueWarEndTime:
        #    util.leagueWarEndTime = util.leagueWarEndTime+86400*14
        data['leagueWarTime'] = util.leagueWarEndTime
        data['nextLeagueWarTime'] = util.leagueWarStartTime
        if data['lastSynTime']==0:
            data['lastSynTime'] = data['serverTime']
        #if data['registerTime']>newbieCup[0]:
        #    data['newbieTime'] = newbieCup[1]
        #data.pop('registerTime')
        data['achieves'] = achieveModule.getAchieves(uid)
        print 'guide', data['guide']
        if data['registerTime'] > settings[3]:
            data['leftDay'] = newUserLogin(uid)
        data['newRewards'] = getUserRewardsNew(uid)
        if data['guide']>=1400:
            days = 0
            if data['registerTime'] < settings[1]:
                days = dailyModule.dailyLogin(uid)
            print 'days', days
            if days>0:
                data['days']=days
                reward = int((50+30*days)**0.5+0.5)
                if version==0 or (days!=7 and days!=14 and days!=30):
                    updateCrystal(uid, reward)
                    if version==0 and (days==7 or days==14 or days==30):
                        dailyModule.loginWithDays(uid, days)
                    data['crystal'] = data['crystal']+reward
                data['reward'] = reward
            ret = checkUserReward(uid, language)
            if ret!=None:
                data['crystal'] = data['crystal']+ret[0]
                data['rewards'] = ret[1]
        loginlogger.info("%s\t%d\tlogin" % (platform,uid))
    else:
        data = getUserInfos(uid)
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
        if build[2]==1002:
            if build[6]!="":
                try:
                    rid = json.loads(build[6])['rid']
                    if data['researches'][rid-1]==5:
                        build[6]=""
                        repairDatas.append([build[0],""])
                except:
                    print "research data error"
        elif build[2]==2004:
            try:
                check = json.loads(build[6])
                if check['resource'] == 0:
                    errorBuilderNum = errorBuilderNum+1
                    builders.append(build)
            except e:
                print e

            #if build[6]=='{"resource":0}':
        if build[4]>0:
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
        data['builds'] = getUserBuilds(eid)
        data['code'] = 0
        return json.dumps(data)

@app.route("/getReplay", methods=['GET'])
def getReplay():
    vid = int(request.args.get("vid"))
    return queryOne("SELECT replay FROM nozomi_replay WHERE id=%s", (vid))[0]

@app.route("/kxlogin", methods=['POST'])
def loginKaiXin():
    key=request.form.get("k")
    secret=request.form.get("s")
    platform = request.form.get("plat","ios")
    t = int(time.mktime(time.localtime()))
    params="client_id=10008&command=getbinduid&key=%s&secret=%s&time=%d&version=1.0" % (key, secret, t)
    sign = md5(params + "&7ca082479115b5653816c87eb75a3054").hexdigest()
    rurl = "http://api.loftygame.com/api.php?%s&sign=%s" % (params, sign)
    print "loginUrl", rurl
    req = urllib2.Request(rurl)
    page = urllib2.urlopen(req)
    rawdata = page.read()
    print "raw", rawdata
    data = json.loads(rawdata)
    print data
    if data['ret']==1:
        ret = dict(code=0, kxid=data['data']['uid'])
        if platform!="android":
            ret['products'] = {"com.loftygame.500crystals":500,"com.loftygame.1200crystals":1200,"com.loftygame.2500crystals":2500,"com.loftygame.6500crystals":6500,"com.loftygame.14000crystals":14000}
            ret['otherpay'] = 1
            ret['released'] = 1
        else:
            ret['products'] = {"com.loftygame.500crystals":"HK$39.00,500","com.loftygame.1200crystals":"HK$77.00,1200","com.loftygame.2500crystals":"HK$155.00,2500","com.loftygame.6500crystals":"HK$387.00,6500","com.loftygame.14000crystals":"HK$775.00,14000"}
        return json.dumps(ret)
    else:
        return json.dumps(dict(code=data['code'],error=data['error']))

@app.route("/getRewards", methods=['GET'])
def getRewards():
    uid = request.args.get('uid', 0, type=int)
    if uid==0:
        return json.dumps(dict(code=1))
    else:
        return json.dumps(dict(code=0, rewards=getUserRewardsNew(uid)))

@app.route("/getBulletins", methods=['GET'])
def getButtetins():
    tmp = queryAll("SELECT text FROM nozomi_bulletin WHERE state=0 ORDER BY `index`")
    bulletins = [r[0] for r in tmp]
    return json.dumps(bulletins)

@app.route("/kxverify", methods=['GET'])
def verifyKaiXin():
    code = 0
    reason = ""
    uid = request.args.get('uid', 0, type=int)
    tid = request.args.get('transactionId','')
    amount = request.args.get('amount', 0, type=int)
    roleId = request.args.get('roleId', 0, type=int)
    serverId = request.args.get('serverId', 0, type=int)
    hash = request.args.get('hash', '')
    sign = md5("%d%s%d%d%d100087ca082479115b5653816c87eb75a3054" % (uid,tid,amount,roleId,serverId)).hexdigest()
    print request.args
    print ("%d%s%d%d%d100087ca082479115b5653816c87eb75a3054" % (uid,tid,amount,roleId,serverId))
    print sign
    if uid==0 or amount==0 or roleId==0:
        code = 1
        reason = "Invalid param"
    elif hash!=sign:
        code = 2
        reason = "Check hash error"
    else:
        uinfo = queryOne("SELECT totalCrystal FROM `nozomi_user` WHERE id=%s",(roleId))
        if uinfo==None:
            code = 1
            reason = "Invalid param"
        else:
            ret = queryOne("SELECT * FROM `nozomi_purchase_record` WHERE transactionId=%s", (tid))
            if ret==None:
                update("INSERT INTO `nozomi_purchase_record` (transactionId,userId,amount) VALUES (%s,%s,%s)", (tid,roleId,amount))
                rewards = [[roleId,0,amount]]
                platform="ios"
                if serverId==1:
                    platform="android_kaixin"
                crystallogger.info("%s\t%d\t%s" % (platform, roleId, json.dumps([-1,int(time.mktime(time.localtime())),amount,uinfo[0]+amount])))
                if uinfo[0]==0:
                    rewards.append([roleId,2,amount])
                executemany("INSERT INTO `nozomi_reward_new` (uid,type,rtype,rvalue,info) VALUES (%s,%s,0,%s,'')", rewards)
                update("UPDATE `nozomi_user` SET totalCrystal=%s WHERE id=%s", (uinfo[0]+amount,roleId))
            else:
                code = 3
                reason = "Duplicate purchase"
    print code, reason
    if code==0:
        return json.dumps(dict(ret=1))
    else:
        return json.dumps(dict(ret=0, code=code,error=reason))

@app.route("/verify", methods=['POST'])
def verifyIAP():
    receipt = request.form.get("receipt")
    uid = request.form.get('uid', 0, type=int)
    if receipt!=None:
        postData = json.dumps({'receipt-data':receipt})
        url = "https://buy.itunes.apple.com/verifyReceipt"
        #url = "https://sandbox.itunes.apple.com/verifyReceipt"
        req = urllib2.Request(url,postData)
        rep = urllib2.urlopen(req)
        page = rep.read()
        #update("INSERT INTO `buyCrystalVerify` (verify_code,verify_result) VALUES(%s,%s)", (receipt,page))
        result = json.loads(page)
        print uid, receipt
        if result['status']==21007:
            url = "https://sandbox.itunes.apple.com/verifyReceipt"
            req = urllib2.Request(url,postData)
            rep = urllib2.urlopen(req)
            page = rep.read()
            result = json.loads(page)
            
        if result['status']==0:
            receipt = result['receipt']
            if int(receipt['original_purchase_date_ms'][:-3])>int(time.mktime(time.localtime())-86400):
                uniqInsert = update("INSERT IGNORE INTO `nozomi_iap_record` (transaction_id, buy_item, verify_data, uid) VALUES(%s,%s,%s,%s)",(receipt['original_transaction_id'],receipt['product_id'],page,uid))
                #uniqInsert = 1
                if uniqInsert>0:
                    if uid>0:
                        crystal = [500,1200,2500,6500,14000,200,0][int(receipt['product_id'][-1:])]
                        updateCrystal(uid, crystal)
                    return "success"
    return "fail"

@app.route("/synData", methods=['POST'])
def synData():
    print 'synData', request.form
    uid = int(request.form.get("uid", 0))
    if uid==0:
        return json.dumps({'code':401})
    platform = "ios"
    if 'platform' in request.form:
        platform = request.form['platform']
    oldCrystal = getUserAllInfos(uid)['crystal']
    newCrystal = oldCrystal
    userInfoUpdate = dict(lastSynTime=int(time.mktime(time.localtime())))
    if 'userInfo' in request.form:
        userInfo = json.loads(request.form['userInfo'])
        userInfoUpdate.update(userInfo)
        if 'score' in userInfo:
            userInfoUpdate.pop('score')
        if 'shieldTime' in userInfo:
            setUserShield(uid, userInfo['shieldTime'])
        if 'crystal' in userInfo:
            newCrystal = userInfo['crystal']
    changeCrystal = 0
    if 'cc' in request.form:
        baseCrystal = request.form.get('bs',0,type=int)
        changeCrystal = request.form.get('cc',0,type=int)
        if baseCrystal>oldCrystal+100 or changeCrystal>100000:
            return '{"code":1}'
        newCrystal = baseCrystal+changeCrystal
        userInfoUpdate['crystal'] = newCrystal
    if 'crystal' in request.form:
        ls = json.loads(request.form['crystal'])
        allAdd = 0
        for l in ls:
            if l[0]==-1:
                allAdd = allAdd+l[2]
            else:
                allAdd = allAdd-l[2]
        if (changeCrystal>0 and allAdd+200<changeCrystal) or (oldCrystal+allAdd-newCrystal<=-200):
            testlogger.info("[crystal]BadSynData\t%d\t%d\t%d" % (uid, oldCrystal, newCrystal))
        for l in ls:
            if l[0]>0:
                crystallogger.info("%s\t%d\t%s" % (platform, uid, json.dumps(l)))
    elif changeCrystal==0 and newCrystal-oldCrystal>=200:
        testlogger.info("[crystal]BadSynData\t%d\t%d\t%d" % (uid, oldCrystal, newCrystal))
    if 'days' in request.form:
        days = int(request.form['days'])
        dailyModule.loginWithDays(uid, days)
    if 'grl' in request.form:
        getRewardList = json.loads(request.form['grl'])
        deleteUserRewards(getRewardList)
    if 'delete' in request.form:
        delete = json.loads(request.form['delete'])
        deleteUserBuilds(uid, delete)
    if 'achieves' in request.form:
        achieves = json.loads(request.form['achieves'])
        achieveModule.updateAchieves(uid, achieves)
    if 'research' in request.form:
        researches = json.loads(request.form['research'])
        updateUserResearch(uid, researches)
    if 'update' in request.form:
        update = json.loads(request.form['update'])
        for build in update:
            if build[2]==1002:
                ext = build[6]
                util.restoreBuilds(uid)
                oldExt = queryOne("SELECT `extend` FROM nozomi_build WHERE id=%s AND bid=1002", (uid), util.getDBID(uid))
                if oldExt!=None:
                    oldExt = oldExt[0]
                    if oldExt!="" and 'research' not in request.form:
                        build[6]=oldExt
                break
        updateUserBuilds(uid, update)
    updateUserInfoById(userInfoUpdate, uid)
    updateUserState(uid, int(request.form.get("eid", 0)))
    if 'stat' in request.form:
        statlogger.info("%s\t%d\t%s" % (platform, uid, request.form['stat']))
    if 'bcl' in request.form:
        testlogger.info("[BuyCrystalList]%d\t%s" % (uid, request.form['bcl']))

    loginlogger.info("%s\t%d\tsynData" % (platform,uid))
    return json.dumps({'code':0})

@app.route("/synBattleData", methods=['POST'])
def synBattleData():
    #print 'synBattleData', request.form
    uid = int(request.form.get("uid", 0))
    eid = int(request.form.get("eid", 0))
    incScore = int(request.form.get("score", 0))
    print("test uid and eid %d,%d; score=%d" % (uid, eid, -incScore))
    if uid==0 or eid==0 or incScore>60 or incScore<-60:
        return json.dumps({'code':401})
    baseScore = request.form.get("bscore", 0, type=int)
    ebaseScore = request.form.get("ebscore", 0, type=int)
    if baseScore>0 and ebaseScore>0:
        curScore = getUserInfos(uid)['score']
        if curScore!=baseScore:
            return json.dumps(dict(code=1, reason="duplicate request"))
        else:
            UserRankModule.newUpdateScore(uid, eid, baseScore-incScore, ebaseScore+incScore)
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
        #baseScore = getUserInfos(eid)['score']
        #userInfoUpdate=dict(score=baseScore+incScore)

        if 'shieldTime' in request.form:
            t = int(request.form['shieldTime'])
            #userInfoUpdate['shieldTime'] = t
            setUserShield(eid, t)
            userInfoUpdate=dict(shieldTime=t)
            updateUserInfoById(userInfoUpdate, eid)
        #updateUserInfoById(userInfoUpdate, eid)
    #if incScore!=0:
    #    myScore = getUserInfos(uid)['score']-incScore
    #    userInfoUpdate=dict(score=myScore)
    #    updateUserInfoById(userInfoUpdate, uid)
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
            print "insert history filter"
            update("INSERT INTO nozomi_battle_history (uid, eid, videoId, `time`, `info`, reverged) VALUES(%s,%s,%s,%s,%s,%s)", (eid, uid, videoId, int(time.mktime(time.localtime())), util.filter4utf8(request.form['history']), reverged))
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
    eid = int(request.form.get('eid', 0))
    ClanModule.clearBattleStateAtOnce(eid)
    return json.dumps(dict(code=0))

@app.route("/getLeagueRank", methods=['GET'])
def getLeagueRank():
    return json.dumps(ClanModule.getTopClans())

@app.route("/getCaesarsCupRank", methods=['GET'])
def getCaesarsCupRank():
    return json.dumps(ClanModule.getTopClans2())

@app.route("/getNewbieRank", methods=['GET'])
def getNewbieRank():
    return json.dumps(getTopNewbies())
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

#@app.route('/getAllUnPaiedRecord', methods=['GET'])
#def getAllUnPaiedRecord():
#    uid = request.args
    
#client syn the lua error to server
@app.route("/synLuaError", methods=['POST'])
def synLuaError():
    uid = request.form.get('uid', 0, type=int)
    error = request.form.get("error","")
    platform = request.form.get("error","")
    testlogger.info("userId:%d,platform:%s\n%s" % (uid,platform,error))
    return "success"
@app.route('/updateTime')
def updateTime():
    start = queryOne('select value from activity where `key` = "startTime"')[0]
    end = queryOne('select value from activity where `key` = "endTime"')[0]
    util.leagueWarStartTime =  int(time.mktime(json.loads(start)))
    util.leagueWarEndTime = int(time.mktime(json.loads(end))) 
    return jsonify(dict(code=1))

app.secret_key = os.urandom(24)
app.config['MAX_CONTENT_LENGTH'] = 16*1024*1024
app.wsgi_app = ProxyFix(app.wsgi_app)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port = config.HOSTPORT)
