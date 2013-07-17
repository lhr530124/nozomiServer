#coding:utf8
import sys
sys.path.append('..')
import MySQLdb
import config
import redis

def getConn():
    return MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
myCon = getConn()



rserver = redis.Redis()

myCon.query('flush tables with read lock')
sql = 'select * from nozomi_rank'
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
for i in res:
    rserver.zadd('userRank', i['uid'], i['score'])

myCon.query('unlock table')

myCon.close()
    

