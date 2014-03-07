#coding:utf8
#!/bin/python
import json
import MySQLdb
import time
import sys
sys.path.append('..')
import config
#import util
import os

myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
cur = myCon.cursor()

sql = 'delete from nozomi_build from where id = 1'
cur.execute(sql)

f = open('caedata.json')
b = f.read()
b = json.loads(b)
for i in b:
    sql = 'insert ignore into nozomi_build (`extend`, `level`, `bid`, `state`, `grid`, `time`, `hitpoints`, `id`, `buildIndex` ) values(%s, %s, %s, %s, %s, %s, %s, %s, %s) '
    cur.execute(sql, (i['extend'], i['level'], i['bid'], i['state'], i['grid'], i['time'], i['hitpoints'], i['id'], i['buildIndex']))


myCon.commit()
myCon.close()

