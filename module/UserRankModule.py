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
redisPool2 = redis.ConnectionPool(host="10.168.124.83")
def getServer():
    rserver = redis.StrictRedis(connection_pool=redisPool)
    return rserver
def getServer2():
    rserver = redis.StrictRedis(connection_pool=redisPool2)
    return rserver

def updateZombieCount(uid, newKill):
    if uid>0 and newKill!=0:
        rserver = getServer()
        rserver.zincrby("zombie",uid,newKill)
        rserver.zincrby("zombieRank",uid,newKill)
        rserver2 = getServer2()
        rserver2.zincrby("zombie",uid,newKill)
        rserver2.zincrby("zombieRank",uid,newKill)
