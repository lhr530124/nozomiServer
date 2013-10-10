#coding:utf8
import time
import config
from flaskext import *
beginTime = (2013, 1, 1, 0, 0, 0, 0, 0, 0)
beginTime = int(time.mktime(beginTime))
def getTime():
    return int(time.time()-beginTime)

def getToday():
    nt = time.localtime()
    today = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 ))
    return today-beginTime

def getYesterday():
    nt = time.localtime()
    yesterday = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday-1, 0, 0, 0, 0, 0, 0 ))
    return yesterday-beginTime

def getAbsToday():
    nt = time.localtime()
    today = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 ))
    return today

def getAbsYesterday():
    nt = time.localtime()
    yesterday = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday-1, 0, 0, 0, 0, 0, 0 ))
    return yesterday

#奇数偶数
def getDBID(uid):
    return (uid+1)%2

    """
    #print "getDBID", uid, config.userCut
    for i in xrange(0, len(config.userCut)):
        if uid <= config.userCut[i]:
            #print 'return', i
            return i
    #print 'return 2', len(config.userCut)-1
    return len(config.userCut)-1
    """

#将用户的建筑物数据 从主数据库 恢复到 对应的cong 数据库 
#0 是主数据库
#主 数据库 
#对even 数据库的数据 也要做备份 1 2 
#访问建筑之前 首先执行一下restoreBuilds
def restoreBuilds(uid):
    did = getDBID(uid)
    #主数据库用户
    if did == 0:
        return
    #检查从服务器上是否有这个用户的建筑物
    num = queryAll('select id from nozomi_build where id = %s limit 1', (uid), did)
    #从主拷贝到nozomi2 数据库中
    if num == None:
        res = queryAll('select id, buildIndex, grid, state, bid, level, `time`, hitpoints, extend from nozomi_build where id = %s', (uid), 0)
        executemany("INSERT ignore INTO nozomi_build (id, buildIndex, grid, state, bid, level, `time`, hitpoints, extend) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)", res, did)
    return



    

import re
def filter4utf8(s):
    print "filter string"
    highpoints = re.compile(u'[\U00010000-\U0010ffff]')
    return highpoints.sub(u'', s)

    
