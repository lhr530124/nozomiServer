#coding:utf8
import MySQLdb
from DBUtils.PooledDB import PooledDB

import sys
sys.path.append('..')

from config import *
"""
HOST = 'localhost'
PASSWD = '2e4n5k2w2x'
"""

class DbManager:

    def __init__(self):
        connKwargs = {'host':HOST,'user':'root','passwd':PASSWORD,'db':'nozomi','charset':"utf8"}
        self._pool = PooledDB(MySQLdb, mincached=1, maxcached=10, maxshared=10, maxusage=10000, **connKwargs)
        
        #默认第二个数据库
        connKwargs2 = {'host':HOST,'user':'root','passwd':PASSWORD,'db':'nozomi2','charset':"utf8"}
        self._pool2 = PooledDB(MySQLdb, mincached=1, maxcached=10, maxshared=10, maxusage=10000, **connKwargs2)

        self.allPools = [self._pool, self._pool2]

    def getConn(self, dbID=0):
        return self.allPools[dbID].connection()

_dbManager = DbManager()

def getConn(dbID=0):
    return _dbManager.getConn(dbID=0)

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
    con = getConn(dbID)
    cur = con.cursor()
    cur.executemany(sql, params)
    con.commit()
    cur.close()
    con.close()

def queryOne(sql, params=None):
    con = getConn()
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
    con = getConn(dbID)
    cur = con.cursor()
    rowcount = 0
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
