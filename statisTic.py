#coding:utf8
import MySQLdb 
from flask import Flask, request, g, render_template, _app_ctx_stack
import time
import json
import datetime

import config
app = Flask(__name__)
app.config.from_object("config")

beginTime = [2013, 1, 1, 0, 0, 0, 0, 0, 0]
beginTime = int(time.mktime(beginTime))

def getConn():
    top = _app_ctx_stack.top
    if not hasattr(top, 'db'):
        top.db = MySQLdb.connect(host=app.config['HOST'], user='root', passwd=app.config['PASSWORD'], db=app.config['DATABASE'], charset='utf8')
    return top.db

@app.teardown_appcontext
def closeConn(excep):
    top = _app_ctx_stack.top
    if hasattr(top, 'db'):
        top.db.close()
    
@app.route('/getRegister')
def getRegister():
    myCon = getConn()
    #一天内注册的用户数量
    now = int(time.time())-beginTime
    allData = []
    for i in xrange(1, 8):
        sql = 'select count(*) from nozomi_user where (%d-registerTime) < 24*3600*(8-%d) and (%d-registerTime) >= 24*3600*(7-%d)  ' % (now, i, now, i)
        myCon.query(sql)
        res = myCon.store_result().fetch_row(0, 0)
        allData.append({'num':res[0][0], 'day':8-i})

    #myCon.close()
    return render_template("showData.html", data=allData, title=u"注册")
    #return json.dumps(res)

@app.route('/getDAU')
def getDAU():
    myCon = getConn()
    now = int(time.time())
    allData = []
    for i in xrange(1, 8):
        sql = 'select count(*) from nozomi_user where lastSynTime >= %d and lastSynTime < %d' % (now-24*3600*(8-i), now-24*3600*(7-i)) 
        print sql
        myCon.query(sql)
        res = myCon.store_result().fetch_row(0, 0)
        allData.append({'num':res[0][0], 'day':8-i})
    return render_template("showData.html", data=allData, title="DAU")

@app.route('/getIncome')
def getIncome():
    myCon = getConn()
    now = time.localtime()
    allData = []
    for i in xrange(7, -1, -1):
        lastDay = now.tm_mday-i
        nearDay = now.tm_mday-(i-1)
        lastDay = time.localtime(time.mktime((now.tm_year, now.tm_mon, lastDay, now.tm_hour, now.tm_min, now.tm_sec, 0, 0, 0)))
        nearDay = time.localtime(time.mktime((now.tm_year, now.tm_mon, nearDay, now.tm_hour, now.tm_min, now.tm_sec, 0, 0, 0)))
        sql = 'select count(*), sum(crystal) from buyCrystal where `time` > "%d-%d-%d" and `time` <= "%d-%d-%d"' % (lastDay.tm_year, lastDay.tm_mon, lastDay.tm_mday,  nearDay.tm_year, nearDay.tm_mon, nearDay.tm_mday)
        print sql
        myCon.query(sql)
        res = myCon.store_result().fetch_row(0, 0)
        print res

        allData.append(["%s-%s-%s  %s-%s-%s"%(lastDay.tm_year, lastDay.tm_mon, lastDay.tm_mday,  nearDay.tm_year, nearDay.tm_mon, nearDay.tm_mday)
 , res[0][0], int(res[0][1] or 0)])
    
    return render_template("showCrystal.html", data=allData)
     

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.STATISTIC_PORT)
