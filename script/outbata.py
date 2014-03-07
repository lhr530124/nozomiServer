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
sql = 'select * from nozomi_build where id = 1'
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
res = json.dumps(res)

f = open('caedata.json', 'w')
f.write(res)
f.close()

myCon.close()
