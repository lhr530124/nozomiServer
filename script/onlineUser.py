#coding:utf8
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import logging

from logging.handlers import TimedRotatingFileHandler

numbHandler = TimedRotatingFileHandler('online.log', 'd', 7)
numLog = logging.getLogger("numLog")
numLog.addHandler(numbHandler)
numLog.setLevel(logging.INFO)


while True:
    now = int(time.time())
    myCon = MySQLdb.connect(host=config.HOST, user=config.USER, passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
    sql = 'select count(*) from nozomi_user where lastSynTime >= %d' % (now-300)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 0)
    numLog.info("%s %s"% (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), res[0][0]))
    myCon.close()
    time.sleep(300)
