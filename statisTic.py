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
    now = time.time()
    allData = []
    for i in xrange(1, 8):
        minDay = now-24*3600*(8-i)
        maxDay = now-24*3600*(7-i)
        maxDay = time.localtime(maxDay)
        minDay = time.localtime(minDay)
        print maxDay
        print minDay
        sql = 'select count(*) from nozomi_user_login where loginDate >= "%d-%d-%d" and loginDate < "%d-%d-%d"' % (minDay.tm_year, minDay.tm_mon, minDay.tm_mday, maxDay.tm_year, maxDay.tm_mon, maxDay.tm_mday)
        print sql
        myCon.query(sql)
        res = myCon.store_result().fetch_row(0, 0)
        allData.append({'num':res[0][0], 'day':8-i})
    return render_template("showData.html", data=allData, title="DAU")
    
     

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=config.STATISTIC_PORT)
