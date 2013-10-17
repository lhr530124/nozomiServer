#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os
import time
import json

#startTime = sys.argv[1]
#endTime = sys.argv[2]

myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')

sql = 'select value from activity where `key` = "startTime"'
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
oldStart = res[0]["value"]

sql = 'select value from activity where `key` = "endTime"'
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
oldEnd = res[0]["value"]

oldStart = json.loads(oldStart)
oldStart = time.mktime(oldStart)
oldEnd = json.loads(oldEnd)
oldEnd = time.mktime(oldEnd)

now = time.time()
if now > oldStart+24*3600*12:
    startTime = oldStart+24*3600*14
    endTime = oldEnd+24*3600*14

    startTime = time.localtime(startTime)
    endTime = time.localtime(endTime)

    startTime = "[%d,%d,%d,0,0,0,0,0,0]" % (startTime.tm_year, startTime.tm_mon, startTime.tm_mday)
    endTime = "[%d,%d,%d,0,0,0,0,0,0]" % (endTime.tm_year, endTime.tm_mon, endTime.tm_mday)

    print "start end", startTime, endTime

    #清空 积分
    #设置所有web服务器的活动数据
    sql = 'update nozomi_clan set score2 = 0'
    myCon.query(sql)

    sql = 'update activity set value = "%s" where `key` = "startTime"' % (startTime)
    myCon.query(sql)

    sql = 'update activity set value = "%s" where `key` = "endTime"' % (endTime)
    myCon.query(sql)

    myCon.commit()

    #激活服务器更新 
    #request rr to update each server use nginx configure to handler
    import urllib
    r = 'http://localhost:9791/updateTime'
    q = urllib.urlopen(r)
    s = q.read()
    print s

myCon.close()

