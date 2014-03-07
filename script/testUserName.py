#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
#import util
import os

myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
cur = myCon.cursor()
import json
sql = 'insert into activity (`key`, `value`) values ("startTime", "[2014, 2,2, 0, 0, 0, 0, 0, 0]")'
cur.execute(sql)
sql = 'insert into activity (`key`, `value`) values ("endTime", "[2014, 2,7, 0, 0, 0, 0, 0, 0]")'
cur.execute(sql)


f = open('uname.json')
u = f.read()
u = json.loads(u)
for i in u:
    sql = 'update nozomi_user set name = %s where id = %s'
    cur.execute(sql, (i['name'], i['id']))
    

f = open('bdata.json')
b = f.read()
b = json.loads(b)
for i in b:
    sql = 'insert ignore into nozomi_build (`extend`, `level`, `bid`, `state`, `grid`, `time`, `hitpoints`, `id`, `buildIndex` ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s) '
    cur.execute(sql, (i['extend'], i['level'], i['bid'], i['state'], i['grid'], i['time'], i['hitpoints'], i['id'], i['buildIndex']))
    

myCon.commit()
myCon.close()
