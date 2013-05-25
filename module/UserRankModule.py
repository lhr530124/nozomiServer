#coding:utf8

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

    #增加新得分人数 多个服务器同时 并行操作修改 存在锁的问题
    sql = 'insert nozomi_score_count (`score`, `count`) values (%d, 1) on duplicate key update count = count+1 ' % (newScore)
    myCon.query(sql)
    myCon.commit()

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
def getUser(myCon, rank):
    total = 0
    sql = 'select * from nozomi_score_count order by score desc'
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    
    lastScore = -1
    lastTotal = 0
    for i in res:
        lastScore = i['score']
        total += i['count']
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
    sql = 'select * from nozomi_score_count order by score desc'
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    
    lastScore = -1
    lastTotal = 0
    startIndex = 0
    for i in res:
        lastScore = i['score']
        total += i['count']
        if total > start:
            break
        lastTotal = total
        startIndex += 1

    
    leftNum = start - lastTotal
    curIndex = startIndex
    limitLength = rangeLength
    while curIndex < len(res):
        curScore = res[curIndex]['score']
        sql = 'SELECT r.uid, r.score, r.lastRank, u.name FROM nozomi_rank as r, nozomi_user as u WHERE r.score = %d AND r.uid=u.id limit %d , %d' % (curScore, leftNum, limitLength)
        myCon.query(sql)
        users = myCon.store_result().fetch_row(0, 1)
        allUser += users
        
        leftNum = 0
        curIndex += 1
        limitLength -= len(users)

    return allUser
