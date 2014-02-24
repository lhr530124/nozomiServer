#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os

myCon = MySQLdb.connect(host=config.HOST, user=config.USER, passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')

sql = 'select * from nozomi_user where id < 1000' 
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
import json
udata = json.dumps(res)
f = open('uname.json', 'w')
f.write(udata)
f.close()

sql = 'select * from nozomi_build where id < 1000'
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
bdata = json.dumps(res)
f = open('bdata.json', 'w')
f.write(bdata)
f.close()


