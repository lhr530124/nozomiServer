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

myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
sql = 'update nozomi_clan set score2 = 0'
myCon.query(sql)
myCon.commit()
myCon.close()
