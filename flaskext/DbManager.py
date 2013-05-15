import MySQLdb
from DBUtils.PooledDB import PooledDB

class DbManager:

    def __init__(self):
        connKwargs = {'host':'127.0.0.1','user':'root','passwd':'3508257','db':'nozomi','charset':"utf8"}
        self._pool = PooledDB(MySQLdb, mincached=1, maxcached=10, maxshared=10, maxusage=10000, **connKwargs)

    def getConn(self):
        return self._pool.connection()

_dbManager = DbManager()

def getConn():
    return _dbManager.getConn()

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

def executemany(sql, params):
    con = getConn()
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

def queryAll(sql, params=None):
    con = getConn()
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
