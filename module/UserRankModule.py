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
sys.path.append('..')
import config
import redis
import sys
sys.path.append('..')
import config
def getServer():
    rserver = redis.Redis(host=config.REDIS_HOST)
    return rserver

#cold synchronize database and redis
#extra script do it!
def initScoreCount(myCon):
    #no need to init sortedScore
    #uid score ---> redis
    #sql = 'select * from nozomi_rank'


    """
    sql = 'select * from nozomi_score_count order by score desc'
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    for i in res:
        scoreCount[i['score']] = i['count']
        sortedScore.append(i['score'])
    sortedScore.sort(reverse=True)
    """

def initUserScore(myCon, uid, score):
    sql = 'insert into  nozomi_rank (uid, score) values(%d, %d)' % (uid, score)
    myCon.query(sql)
    myCon.commit()
    

    
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

def updateScore(myCon, uid, newScore):
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

#得到某个得分的用户的 排名
#并列排名的用户的排名是相同的
"""
def getRank(myCon, score):
    
    sql = 'select sum(`count`) from nozomi_score_count where score > %d' % (score)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 0)
    if len(res) > 0:
        if res[0][0] != None:
            return int(res[0][0])
    return 0
"""

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

    """
    total = 0
    #sql = 'select * from nozomi_score_count order by score desc'
    #myCon.query(sql)
    #res = myCon.store_result().fetch_row(0, 1)
    
    lastScore = -1
    lastTotal = 0
    for i in sortedScore:
        lastScore = i
        total += scoreCount[i]
        if total > rank:
            break
        lastTotal = total
    

    #lastScore 该排名 的得分
    #lastTotal 该排名 得分之前 用户数量
    #根据数据库返回的排名人数
    #数据库可能返回失败？ 
    leftNum = rank - lastTotal
    sql = 'select * from nozomi_rank where score = %d limit %d , 1' % (lastScore, leftNum)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    r = res[0]['uid']
    return r
    """

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

