#coding:utf8
#import bisect
#单独服务处理排名将排名数据放到内存里面数据库保持一份
#score --->count
#newScore
#oldScore
#sort 排序 bisect 插入排序
scoreCount = {}
#得分排序 从小到大排序
sortedScore = []
def initScoreCount(myCon):
    sql = 'select * from nozomi_score_count order by score desc'
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    for i in res:
        scoreCount[i['score']] = i['count']
        sortedScore.append(i['score'])
    sortedScore.sort(reverse=True)


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
    oldScore = -1
    #获得用户旧的得分
    sql = 'select * from nozomi_rank where uid = %d' % (uid)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    if len(res) > 0:
        oldScore = res[0]['score']

    #更新用户的得分
    sql = 'update nozomi_rank set score = %d where uid = %d' % (newScore, uid)
    myCon.query(sql)

    #减少旧得分人数 多个服务器同时修改count值 存在锁的问题 
    sql = 'update nozomi_score_count set count = count - 1 where score = %d' % (oldScore)
    myCon.query(sql)
    scoreCount[oldScore] -= 1

    #增加新得分人数 多个服务器同时 并行操作修改 存在锁的问题
    sql = 'insert nozomi_score_count (`score`, `count`) values (%d, 1) on duplicate key update count = count+1 ' % (newScore)
    myCon.query(sql)
    myCon.commit()
    if newScore in scoreCount:
        scoreCount[newScore] += 1
    else:
        scoreCount[newScore] = 1
        myInsort(sortedScore, newScore)
        #bisect.insort_right(sortedScore, newScore)


#得到某个得分的用户的 排名
#并列排名的用户的排名是相同的
def getRank(myCon, score):
    sql = 'select sum(`count`) from nozomi_score_count where score > %d' % (score)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 0)
    if len(res) > 0:
        if res[0][0] != None:
            return int(res[0][0])
    return 0

#得到某个排名的用户 score count
#可以把排名数据整个放到内存里面 score count
#排名从0开始
#相同得分的如何返回排名

#rank 可以优化 数据库内部计算count 减少返回的数据量
def getUser(myCon, rank):
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

#得到某个阶段排名所有用户[start, end) [0, 1) = 0
#允许并列排名的学生 0  1 1 3 
def getRange(myCon, start, end):
    rangeLength = end - start
    allUser = []
    #得到排名start 位置的得分
    total = 0
    #sql = 'select * from nozomi_score_count order by score desc'
    #myCon.query(sql)
    #res = myCon.store_result().fetch_row(0, 1)
    
    lastScore = -1
    lastTotal = 0
    startIndex = 0
    for i in sortedScore:
        lastScore = i
        total += scoreCount[i]
        if total > start:
            break
        lastTotal = total
        startIndex += 1

    
    leftNum = start - lastTotal
    curIndex = startIndex
    limitLength = rangeLength
    while curIndex < len(sortedScore):
        curScore = sortedScore[curIndex]
        sql = 'SELECT r.uid, r.score, r.lastRank, u.name FROM nozomi_rank as r, nozomi_user as u WHERE r.score = %d AND r.uid=u.id limit %d , %d' % (curScore, leftNum, limitLength)
        myCon.query(sql)
        users = myCon.store_result().fetch_row(0, 1)
        allUser += users
        
        leftNum = 0
        curIndex += 1
        limitLength -= len(users)

    return allUser
