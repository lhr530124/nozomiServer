#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os

myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
#清空 积分
#设置所有web服务器的活动数据
sql = 'update nozomi_clan set score2 = 0'
myCon.query(sql)
myCon.commit()
myCon.close()

