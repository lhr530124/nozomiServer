#coding:utf8
import MySQLdb
from DBUtils.PooledDB import PooledDB

import sys
sys.path.append('..')

#from config import *
import config

class DbManager:

    def __init__(self):
        self.allPools = []
        for i in xrange(0, len(config.dbInfo)):
            connKwargs = {'host':config.dbInfo[i]['host'],'user':config.dbInfo[i]['user'],'passwd':config.dbInfo[i]['passwd'],'db':config.dbInfo[i]['db'],'charset':"utf8"}
            pool = PooledDB(MySQLdb, mincached=1, maxcached=10, maxshared=10, maxusage=10000, **connKwargs)
            self.allPools.append(pool)
            #print "pool is", pool
        
        #默认第二个数据库
        #connKwargs2 = {'host':HOST,'user':'root','passwd':PASSWORD,'db':'nozomi2','charset':"utf8"}
        #self._pool2 = PooledDB(MySQLdb, mincached=1, maxcached=10, maxshared=10, maxusage=10000, **connKwargs2)

        #self.allPools = [self._pool, self._pool2]

    def getConn(self, dbID=0):
        #print "getConn", dbID
        return self.allPools[dbID].connection()

_dbManager = DbManager()

def getConn(dbID=0):
    return _dbManager.getConn(dbID=dbID)

def insertAndGetId(sql, params=None):
    con = getConn()
    cur = con.cursor()
    if params == None:
        cur.execute(sql)
    else:
        cur.execute(sql, params)
    con.commit()
    id = cur.lastrowid
    cur.close()
    con.close()
    return id

def update(sql, params=None):
    con = getConn()
    cur = con.cursor()
    rowcount = 0
    if params == None:
        rowcount = cur.execute(sql)
    else:
        rowcount = cur.execute(sql, params)
    con.commit()
    cur.close()
    con.close()
    return rowcount

def executemany(sql, params, dbID=0):
    #print "executemany",sql, params, dbID
    con = getConn(dbID=dbID)
    cur = con.cursor()
    cur.executemany(sql, params)
    con.commit()
    cur.close()
    con.close()

def queryOne(sql, params=None, dbID=0):
    con = getConn(dbID=dbID)
    cur = con.cursor()
    rowcount = 0
    if params == None:
        rowcount = cur.execute(sql)
    else:
        rowcount = cur.execute(sql, params)
    ret = None
    if rowcount>0:
        ret = cur.fetchone()
    cur.close()
    con.close()
    return ret

def queryAll(sql, params=None, dbID=0):
    con = getConn(dbID=dbID)
    cur = con.cursor()
    rowcount = 0
    #print "queryAll", params, dbID
    if params == None:
        rowcount = cur.execute(sql)
    else:
        rowcount = cur.execute(sql, params)
    ret = None
    if rowcount>0:
        ret = cur.fetchall()
    cur.close()
    con.close()
    return ret
