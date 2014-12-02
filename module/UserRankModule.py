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
