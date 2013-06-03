# -*- coding: utf8 -*-
import time
import random
from flaskext import *

beginTime = time.mktime((2013,1,1,0,0,0,0,0,0))
def getTime():
    return int(time.mktime(time.localtime())-beginTime)

def newUserState(uid):
    update("INSERT INTO nozomi_user_state (uid, score, shieldTime, onlineTime, attackTime) VALUES (%s, 500, 0, 0, 0)", (uid))

def setUserShield(uid, shieldTime):
    update("UPDATE nozomi_user_state SET shieldTime=%s WHERE uid=%s", (shieldTime-beginTime, uid))

def clearUserShield(uid):
    update("UPDATE nozomi_user_state SET shieldTime=0 WHERE uid=%s", (uid))

def updateUserOnline(uid):
    update("UPDATE nozomi_user_state SET onlineTime=%s WHERE uid=%s", (getTime()+240, uid))

#减少通讯频率，因此每次请求仅更新一次进攻时间（随着下次请求而取消）
def updateUserAttack(uid):
    update("UPDATE nozomi_user_state SET attackTime=%s WHERE uid=%s", (getTime()+240, uid))

def clearUserAttack(uid):
    update("UPDATE nozomi_user_state SET attackTime=0 WHERE uid=%s", (uid))

def getUserState(uid):
    r = queryOne("SELECT shieldTime, onlineTime, attackTime FROM nozomi_user_state WHERE uid=%s", (uid))
    curTime = getTime()
    ret = dict()
    if r[0]>curTime:
        ret['shieldTime'] = r[0]-curTime
    if r[1]>curTime:
        ret['onlineTime'] = r[1]-curTime
    if r[2]>curTime:
        ret['attackTime'] = r[2]-curTime
    return ret

def findAMatch(uid, score, scoreOff):
    curTime = getTime()
    while scoreOff<4000:
        minScore = score-scoreOff
        maxScore = score+scoreOff

        ids = queryOne("SELECT MIN(uid), MAX(uid) FROM nozomi_user_state WHERE score>%s AND score<%s", (minScore, maxScore))
        if ids!=None:
            minId = ids[0]
            maxId = ids[1]
            if maxId != None and minId!=None:
                cut = random.randint(minId, maxId)
                ret = queryOne("SELECT uid FROM nozomi_user_state WHERE uid>=%s AND uid!=%s AND shieldTime<%s AND attackTime<%s AND onlineTime<%s AND score>%s AND score<%s LIMIT 1", (cut, uid, curTime, curTime, curTime, minScore, maxScore))
                if ret!=None:
                    updateUserAttack(ret[0])
                    return ret[0]
        scoreOff *= 2
    return 0
