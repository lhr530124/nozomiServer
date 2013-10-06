#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os

startTime = sys.argv[1]
endTime = sys.argv[2]

myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
#清空 积分
#设置所有web服务器的活动数据
sql = 'update nozomi_clan set score2 = 0'
myCon.query(sql)

sql = 'update activity set value = "%s" where `key` = "startTime"' % (startTime)
myCon.query(sql)

sql = 'update activity set value = "%s" where `key` = "endTime"' % (endTime)
myCon.query(sql)

myCon.commit()
myCon.close()

#激活服务器更新
import urllib
r = 'http://localhost:9791/updateTime'
q = urllib.urlopen(r)
s = q.read()
print s


