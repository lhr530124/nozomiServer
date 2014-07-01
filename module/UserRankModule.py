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
def getServer():
    rserver = redis.Redis(host=config.REDIS_HOST)
    return rserver

#cold synchronize database and redis
#extra script do it!
def initScoreCount(myCon):
    #no need to init sortedScore
    #uid score ---> redis
    #sql = 'select * from nozomi_rank'
    pass

def initUserScore(uid, score):
    myCon = getConn()
    cur = myCon.cursor()
    cur.execute("INSERT INTO nozomi_rank (uid, score) VALUES (%s, %s)",(uid, score))
    cur.execute("INSERT INTO nozomi_research (id, research) VALUES(%s, '[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]')", (uid))
    cur.execute("INSERT INTO nozomi_user_state (uid, score, shieldTime, onlineTime, attackTime) VALUES (%s, %s, 0, 0, 0)", (uid, score))
    myCon.commit()
    cur.close()
    
    rserver = getServer()
    rserver.zadd('userRank', uid, score)

    

def myInsort(a, x):
    """Insert item x in list a, and keep it sorted assuming a is sorted.

    If x is already in a, insert it to the right of the rightmost x.

    Optional args lo (default 0) and hi (default len(a)) bound the
    slice of a to be searched.
    """
    lo = 0
    hi = len(a)
    while lo < hi:
        mid = (lo+hi)//2
        if x > a[mid]: hi = mid
        else: lo = mid+1
    a.insert(lo, x)

def newUpdateScore(uid, eid, uscore, escore, isWin):
    if uscore<=0:
        uscore = 1
    if escore<=0:
        escore = 1
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
    if isWin:
        cur.execute("UPDATE nozomi_zombie_stat SET battles=battles+1 WHERE id=%s",(uid))
    con.commit()
    cur.close()

def getNozomiZombieStat(uid):
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT zombies, endTime, battles, state, zombies2 FROM nozomi_zombie_stat WHERE id=%s",(uid))
    ret = cur.fetchone()
    ret1 = None
    curTime = int(time.mktime(time.localtime()))
    if ret==None:
        endTime = curTime+10*86400
        cur.execute("INSERT INTO nozomi_zombie_stat (id,zombies,endTime,battles,state,zombies2) VALUES (%s,0,%s,0,0,0)", (uid,endTime))
        ret1 = [6007,endTime,0,0]
    else:
        shouldSetZombie = False
        if ret[1]>curTime:
            if ret[4]>0:
                ret1 = [6008, ret[1], ret[0]-ret[4], 0]
            elif ret[3]==0:
                ret1 = [6007, ret[1], ret[2], ret[3]]
            elif ret[4]==0:
                shouldSetZombie = True
        elif ret[4]==0:
            shouldSetZombie = True
        if shouldSetZombie and ret[0]>0:
            endTime = curTime+10*86400
            cur.execute("UPDATE nozomi_zombie_stat SET zombies2=%s,state=1,endTime=%s WHERE id=%s", (ret[0],endTime,uid))
            ret1 = [6008, endTime, 0, 0]
    con.commit()
    cur.close()
    return ret1

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

actTimes = [[1396087200,1396173600,345600]]
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
    return [actTime[0], actTime[1], 1800]

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
        rserver.zadd('challenge%d' % actid, uid, score)
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
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT zombies FROM nozomi_zombie_stat WHERE id=%s", uid)
    ret = cur.fetchone()
    if ret!=None:
        oldNum = ret[0]
        cur.execute("UPDATE nozomi_zombie_stat SET zombies=%s WHERE id=%s",(oldNum+newKill, uid))
        con.commit()
        rserver = getServer()
        rserver.zadd('zombieRank', uid, oldNum+newKill)
    cur.close()

def updateBattleNum(uid):
    update("UPDATE nozomi_zombie_stat SET battles=battles+1 WHERE id=%s",(uid))

def checkBattleReward(uid, isRewardMode):
    con = getConn()
    cur = con.cursor()
    if isRewardMode:
        cur.execute("SELECT battles,state FROM nozomi_zombie_stat WHERE id=%s", (uid))
        ret = cur.fetchone()
        if ret[0]<100 or ret[1]!=0:
            cur.close()
            return False
        cur.execute("UPDATE nozomi_zombie_stat SET state=1 WHERE id=%s", (uid))
    else:
        cur.execute("INSERT INTO nozomi_zombie_stat (id,zombies,endTime,battles,state,zombies2) VALUES (%s,0,%s,0,0,0) ON DUPLICATE KEY UPDATE state=1", (uid, int(time.mktime(time.localtime()))+12*86400))
    con.commit()
    cur.close()
    return True

def checkZombieReward(uid, isRewardMode):
    con = getConn()
    cur = con.cursor()
    if isRewardMode:
        cur.execute("SELECT zombies-zombies2,zombies2 FROM nozomi_zombie_stat WHERE id=%s", (uid))
        ret = cur.fetchone()
        if ret[0]<5000 or ret[1]<=0:
            cur.close()
            return False
        cur.execute("UPDATE nozomi_zombie_stat SET zombies2=-1 WHERE id=%s", (uid))
    else:
        cur.execute("INSERT INTO nozomi_zombie_stat (id,zombies,endTime,battles,state,zombies2) VALUES (%s,0,%s,0,0,-1) ON DUPLICATE KEY UPDATE zombies2=-1", (uid, int(time.mktime(time.localtime()))+12*86400))
    con.commit()
    cur.close()
    return True

def updateScore(myCon, uid, newScore, force=False):
    #don't care about oldScore
    """
    oldScore = -1
    #获得用户旧的得分
    sql = 'select * from nozomi_rank where uid = %d' % (uid)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    if len(res) > 0:
        oldScore = res[0]['score']
    """
    sql = 'select score from nozomi_rank where uid = %d' % (uid)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    oldScore = 0
    if len(res) > 0:
        oldScore = res[0]['score']
    #积分变动太大了
    print oldScore, newScore
    if not force:
        if abs(newScore-oldScore) > 200:
            return

    #更新用户的得分
    #更新搜索对手表格
    sql = 'update nozomi_rank set score = %d where uid = %d' % (newScore, uid)
    myCon.query(sql)
    sql = 'update nozomi_user_state set score = %d where uid = %d' % (newScore, uid)
    myCon.query(sql)
    sql = 'update nozomi_user set score = %d where id = %d' % (newScore, uid)
    myCon.query(sql)

    myCon.commit()

    #如果使用redis 来做数据持久话 则不用担心锁问题
    rserver = getServer()
    rserver.zadd('userRank',uid, newScore )


#init redis when need 
#by user uid to get Rank
def getRank(myCon, uid):
    rserver = getServer()
    return rserver.zrevrank('userRank', uid)

#获得前50以及自己所在名次
def getZombieRank(uid):
    rserver = getServer()
    srank = rserver.zrevrank('zombieRank', uid)
    con = getConn()
    cur = con.cursor()
    allUsers = []
    uids = rserver.zrevrange('zombieRank', 0, 49)
    sql = "SELECT z.id,z.zombies,0,u.name,c.icon,c.name FROM nozomi_zombie_stat AS z, nozomi_user AS u LEFT JOIN `nozomi_clan` AS c ON u.clan=c.id WHERE z.id=%s AND z.id=u.id"
    for uid in uids:
        cur.execute(sql,(int(uid)))
        allUsers.append(cur.fetchone())
    if srank==None or srank<50 or len(allUsers)<50:
        cur.close()
        return allUsers
    uids = rserver.zrevrange('zombieRank', srank-1, srank+9)
    for i in range(len(uids)):
        if i+srank>50:
            cur.execute(sql,(int(uids[i])))
            item = list(cur.fetchone())
            item.append(i+srank)
            allUsers.append(item)
    cur.close()
    return allUsers

#得到某个排名的用户 score count
#可以把排名数据整个放到内存里面 score count
#排名从0开始
#相同得分的如何返回排名

#rank 可以优化 数据库内部计算count 减少返回的数据量

def getUser(myCon, rank):
    rserver = getServer()
    ret = rserver.zrevrange('userRank', rank, rank)
    if len(ret) == 0:
        return None
    return int(ret[0])

#得到某个阶段排名所有用户[start, end) [0, 1) = 0
#允许并列排名的学生 0  1 1 3 

#get Uids and User data
def getRange(myCon, start, end):
    rserver = getServer()
    temp = rserver.zrevrange('userRank', start, end)
    allUser = []
    for u in temp:
        uid = int(u)
        sql = 'SELECT r.uid, r.score, r.lastRank, u.name, c.name AS cname, c.icon FROM nozomi_rank as r, nozomi_user as u LEFT JOIN `nozomi_clan` AS c ON u.clan=c.id WHERE r.uid = %d AND r.uid=u.id' % (uid)
        myCon.query(sql)
        users = myCon.store_result().fetch_row(0, 1)
        allUser += users
    return allUser

