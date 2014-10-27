#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os
import json

#选择所有score2 > 0 的用户
myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
cur = myCon.cursor()
sql = 'select id,score2 from nozomi_clan where score2 > 0 order by score2 desc limit 100'
cur.execute(sql)
res = cur.fetchall()
num = 0
reward = [10000, 5000, 3000, 100]
for i in res:
    cid = i[0]
    cur.execute('select id, lscore from nozomi_user where clan = %s',(cid,))
    allUser = cur.fetchall()
    totalScore = 0
    for u in allUser:
        totalScore = totalScore+u[1]
    rc = reward[min(len(reward)-1, num)]

    score2 = i[1]
    nu = len(allUser)

    for u in allUser:
        urw = (rc+nu-1)/nu
        if totalScore>0:
            urw = (rc*u[1]+totalScore-1)/totalScore
        if urw>0:
            cur.execute("INSERT INTO nozomi_reward_new (uid,type,rtype,rvalue,info) VALUES (%s,%s,%s,%s,%s)", (u[0],3,0,urw,json.dumps(dict(type="C",sc=1,so=score2,st=u[1],rank=num+1,total=rc))))
            #sql = 'insert into nozomi_reward_new (uid, type, rtype, rvalue, info) values(%d, %d, "%s", "%s")' % (u["id"], urw, "Your League get %d points, ranked %d, received %d crystals as total rewards\nYour Exploit is %d, get %d crystal as rewards" % (score2, num+1, rc, u['lscore'], urw), "你的联盟获得了%d积分，排名%d，奖励%d水晶\n你的联盟功勋为%d，奖励水晶%d" % (score2, num+1, rc, u['lscore'], urw))
            #myCon.query(sql)
            #print sql
    num = num+1

myCon.commit()
myCon.close()
