#coding:utf8
#import bisect
#单独服务处理排名将排名数据放到内存里面数据库保持一份
#score --->count
#newScore
#oldScore

#sort 排序 bisect 插入排序
#scoreCount = {}

#得分排序 从小到大排序
#sortedScore = []
import sys
import time
sys.path.append('..')
import config
import redis
from flaskext import *

redisPool = redis.ConnectionPool(host=config.REDIS_HOST)

def getServer():
    rserver = redis.StrictRedis(connection_pool=redisPool)
    return rserver

def initUserScore(uid, score):
    myCon = getConn()
    cur = myCon.cursor()
    cur.execute("INSERT INTO nozomi_rank (uid, score) VALUES (%s, %s)",(uid, score))
    cur.execute("INSERT INTO nozomi_research (id, research) VALUES(%s, '[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]')", (uid,))
    cur.execute("INSERT INTO nozomi_user_state (uid, score, shieldTime, onlineTime, attackTime) VALUES (%s, %s, 0, 0, 0)", (uid, score))
    myCon.commit()
    cur.close()
    
    rserver = getServer()
    rserver.zadd('userRank', score, uid)

def newUpdateScore(uid, eid, uscore, escore, isWin):
    scores = [[uscore, uid]]
    rserver = getServer()
    rserver.zadd('userRank', uid, uscore)
    if eid>1:
        scores.append([escore, eid])
        rserver.zadd('userRank', eid, escore)
    con = getConn()
    cur = con.cursor()
    cur.executemany("update nozomi_rank set score=%s where uid=%s", scores)
    cur.executemany("update nozomi_user_state set score=%s where uid=%s", scores)
    cur.executemany("update nozomi_user set score=%s where id=%s", scores)
    con.commit()
    cur.close()

def getActivityUser(actid, uid):
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT num1,num2,score FROM nozomi_activity_user WHERE actid=%s AND id=%s", (actid,uid))
    ret = cur.fetchone()
    if ret==None:
        cur.execute("INSERT INTO nozomi_activity_user (actid, id, num1, num2, score) VALUES(%s,%s,5,0,0)",(actid,uid))
        con.commit()
        ret = [5,0,0]
    cur.close()
    return ret

actTimes = [[1396087200,1396173600,345600,1396087200]]
waveScore = [
[0,20,50,85,125,170,220,275,335],
[0,40,100,170,250,340,440,550,670],
[0,60,150,255,375,510,660,825,1005],
[0,80,200,340,500,680,880,1100,1340],
[0,100,250,425,625,850,1100,1425,1775],
[0,120,300,510,750,1020,1370,1750,2210],
[0,190,450,745,1075,1440,1840,2275,2895],
[0,210,550,930,1350,1860,2410,3000,3730],
[0,380,850,1415,2025,2730,3480,4375,5415],
[0,700,1750,3100,4750,6700,8950,11500,14600]
]

def getActivityTime(actid, t):
    actTime = actTimes[actid]
    while actTime[1]<t:
        actTime[0] += actTime[2]
        actTime[1] += actTime[2]
    return [actTime[0], actTime[1], 7200, actTime[2], actTime[3]]

def buyActivityNum(actid, uid, activityNum):
    update("UPDATE nozomi_activity_user SET num1=num1+%s WHERE actid=%s AND id=%s", (activityNum,actid,uid))

def updateActivityState(actid, uid, activityData):
    num2 = activityData[0]
    if num2%10>8 or num2>=100:
        return False
    score = activityData[1]+activityData[2]*activityData[3]+waveScore[num2/10][num2%10]
    if num2%10==8 and num2/10<10:
        num2 = num2+2
    elif num2%10==0:
        num2 = num2+1
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT num1,num2,score FROM nozomi_activity_user WHERE actid=%s AND id=%s", (actid,uid))
    ret = cur.fetchone()
    if ret==None:
        cur.close()
        return False
    else:
        num1 = ret[0]
        if num1>0:
            num1 = num1-1
        if num2<ret[1]:
            num2 = ret[1]
        score += ret[2]
        rserver = getServer()
        rserver.zadd('challenge%d' % actid, score, uid)
        cur.execute("UPDATE nozomi_activity_user SET num1=%s,num2=%s,score=%s WHERE actid=%s AND id=%s", (num1,num2,score,actid,uid))
    con.commit()
    cur.close()
    return True

def getZombieChallengeRank(actid, uid):
    rserver = getServer()
    srank = rserver.zrevrank('challenge%d' % actid, uid)
    con = getConn()
    cur = con.cursor()
    allUsers = []
    uids = rserver.zrevrange('challenge%d' % actid, 0, 49)
    sql = "SELECT au.id,au.num2,au.score,u.name,c.icon,c.name FROM nozomi_activity_user AS au, nozomi_user AS u LEFT JOIN `nozomi_clan` AS c ON u.clan=c.id WHERE au.actid=%s AND au.id=%s AND au.id=u.id"
    for ruid in uids:
        cur.execute(sql,(actid, int(ruid)))
        allUsers.append(cur.fetchone())
    if srank==None or srank<50 or len(allUsers)<50:
        cur.close()
        return allUsers
    uids = rserver.zrevrange('challenge%d' % actid, srank-1, srank+9)
    for i in range(len(uids)):
        if i+srank>50:
            cur.execute(sql,(actid, int(uids[i])))
            item = list(cur.fetchone())
            item.append(i+srank)
            allUsers.append(item)
    cur.close()
    return allUsers

def updateZombieCount(uid, newKill):
    updateRankNormal(uid, "zombie", newKill)
    updateRankNormal(uid, "zombieRank", newKill)

def updateRankNormal(uid, key, cvalue):
    if uid>0 and cvalue!=0:
        try:
            rserver = getServer()
            score = rserver.zscore(key, uid)
            if score==None:
                score = 0
            else:
                score = int(score)
            rserver.zadd(key, score+cvalue, uid)
        except:
            return False
    return True

def getRankNormal(uid, key, topnum):
    if uid>0 and topnum>0:
        rserver = getServer()
        srank = rserver.zrevrank(key, uid)
        con = getConn()
        cur = con.cursor()
        allUsers = []
        uids = rserver.zrevrange(key, 0, topnum-1, True)
        sql = "SELECT u.id,%s,0,u.name,c.icon,c.name FROM nozomi_user AS u LEFT JOIN `nozomi_clan` AS c ON u.clan=c.id WHERE u.id=%s"
        for uid in uids:
            cur.execute(sql,(int(uid[1]), int(uid[0])))
            allUsers.append(cur.fetchone())
        if srank==None or srank<topnum or len(allUsers)<topnum:
            cur.close()
            return allUsers
        uids = rserver.zrevrange(key, srank-1, srank+9, True)
        for i in range(len(uids)):
            if i+srank>topnum:
                cur.execute(sql,(int(uids[i][1]), int(uids[i][0])))
                item = list(cur.fetchone())
                item.append(i+srank)
                allUsers.append(item)
        cur.close()
        return allUsers
    return []
