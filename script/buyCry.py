#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os



while True:
    now = time.localtime()
    yesterDay = time.localtime(time.mktime(now)-86400)

    myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
    cursor = myCon.cursor()

    f = open('buyCry.log', 'a')
    f.write('################ Nozomi daily report --'+time.strftime('%Y-%m-%d %H:%M:%S', yesterDay)+' -- '+time.strftime('%Y-%m-%d %H:%M:%S', now)+'######\n')

    td = time.strftime('%Y-%m-%d', now)
    yd = time.strftime('%Y-%m-%d', yesterDay)

    sql = 'select uid, crystal, `time` from buyCrystal where `time` >= "%s" and `time` < "%s" and crystal >= 500' % (yd, td)
    print sql
    cursor.execute(sql)
    result = cursor.fetchall()
    for r in result:
        f.write('%d %d %s\n' % (r[0], r[1], r[2]))

    sql = 'select count(*) from buyCrystal where `time` >= "%s" and `time`< "%s"  and crystal >= 500' % (yd, td)
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    f.write('Daily number of users who buy cae: %d\n' % (num))

    sql = 'select sum(crystal) from buyCrystal where `time` >= "%s" and `time` < "%s" and crystal >= 500' % (yd, td)
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    num = num or 0
    f.write('Daily crystal buy: %d\n' % (num))


    sql = 'select count(*) from buyCrystal where crystal >= 500'
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    f.write('Total number of users who buy crystal: %d\n'% (num) ) 

    sql = 'select sum(crystal) from buyCrystal where crystal >= 500'
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0] or 0
    f.write('Total crystal: %d\n' % (num))


    beginTime = [2013, 1, 1, 0, 0, 0, 0, 0, 0]
    beginTime = int(time.mktime(beginTime))

    sql = 'select count(*) from nozomi_user where registerTime >= %d and registerTime < %d' % (util.getYesterday(), util.getToday())
    print sql
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    f.write('Daily number of New Users: %d\n' % (num))

    sql = 'select count(*) from nozomi_user where registerTime >= %d and registerTime < %d and guideValue=1400' % (util.getYesterday(), util.getToday())
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    f.write('Daily number of New Users and finish Newbie Task: %d\n' % (num))

    sql = 'select count(*) from nozomi_user' 
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    f.write('Total number of Users: %d\n' % (num))


    sql = 'select count(*) from nozomi_user where lastSynTime >= %d and lastSynTime < %d' % (util.getAbsYesterday(), util.getAbsToday())
    cursor.execute(sql)
    result = cursor.fetchall()
    num = result[0][0]
    f.write('Daily Active Users: %d\n' % (num))
    f.close()
    myCon.close()


    #os.system('cat buyCry.log >> totalCrystal.log')
    #os.system('mv buyCry.log /var/www/html/crystal.log')
    #os.system('cp totalCrystal.log /var/www/html/')
    time.sleep(86400)

    

