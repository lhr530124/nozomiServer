# -*- coding: utf8 -*-
import time
import random
from flaskext import *

beginTime = time.mktime((2013,1,1,0,0,0,0,0,0))
def getTime():
    return int(time.mktime(time.localtime())-beginTime)

def newUserState(uid):
    update("INSERT INTO nozomi_user_state (uid, score, shieldTime, onlineTime, attackTime) VALUES (%s, 500, 0, 0, 0)", (uid,))
    update("INSERT INTO nozomi_user_state (uid, score, shieldTime, onlineTime, attackTime) VALUES (%s, 500, 0, 0, 0)", (uid,), 3)

def setUserShield(uid, shieldTime):
    update("UPDATE nozomi_user_state SET shieldTime=%s WHERE uid=%s", (shieldTime-beginTime, uid))
    update("UPDATE nozomi_user_state SET shieldTime=%s WHERE uid=%s", (shieldTime-beginTime, uid), 3)

def clearUserShield(uid):
    update("UPDATE nozomi_user_state SET shieldTime=0 WHERE uid=%s", (uid,))
    update("UPDATE nozomi_user_state SET shieldTime=0 WHERE uid=%s", (uid,), 3)

def updateUserOnline(uid):
    update("UPDATE nozomi_user_state SET onlineTime=%s WHERE uid=%s", (getTime()+1800, uid))
    update("UPDATE nozomi_user_state SET onlineTime=%s WHERE uid=%s", (getTime()+1800, uid), 3)

#减少通讯频率，因此每次请求仅更新一次进攻时间（随着下次请求而取消）
def updateUserAttack(uid):
    update("UPDATE nozomi_user_state SET attackTime=%s WHERE uid=%s", (getTime()+240, uid))
    update("UPDATE nozomi_user_state SET attackTime=%s WHERE uid=%s", (getTime()+240, uid), 3)

def clearUserAttack(uid):
    update("UPDATE nozomi_user_state SET attackTime=0 WHERE uid=%s", (uid,))
    update("UPDATE nozomi_user_state SET attackTime=0 WHERE uid=%s", (uid,), 3)

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

#uid = 0 user not exist ! so don't return any user info
def findAMatch(uid, score, scoreOff):
    curTime = getTime()
    highScore = 1600
    tryTime = 0
    while tryTime<3:
        tryTime = tryTime+1
        rscore = score+score*random.randint(-50,100)/400
        if rscore>highScore:
            maxScore = 10000
            minScore = rscore-100
            if minScore>highScore:
                minScore = highScore
            #it is a small number, so get all to random
            ids = queryAll("SELECT uid FROM nozomi_user_state WHERE uid!=%s AND shieldTime<%s AND attackTime<%s AND onlineTime<%s AND score>%s AND score<%s", (uid,curTime,curTime,curTime,minScore,maxScore))
            if ids!=None:
                num = len(ids)
                cut = ids[random.randint(0, num-1)][0]
                updateUserAttack(cut)
                return cut
        else:
            maxScore = rscore+50
            minScore = rscore-50
            if minScore<20:
                minScore = 5 
                maxScore = 75
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
    return 1

def findSpecial(uid, level):
    curTime = getTime()
    ids = queryAll("SELECT u.id FROM nozomi_special_users AS u INNER JOIN nozomi_user_state AS s ON u.id=s.uid WHERE s.shieldTime<%s AND s.attackTime<%s AND s.onlineTime<%s AND u.level>=%s AND u.level<=%s", (curTime,curTime,curTime,level-1,level+1))
    if ids!=None and len(ids)>0:
        num = len(ids)
        cut = ids[random.randint(0, num-1)][0]
        updateUserAttack(cut)
        return cut
    else:
        return findAMatch(uid, 1600, 200)
