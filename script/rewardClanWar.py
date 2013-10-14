#coding:utf8
#!/bin/python
import MySQLdb
import time
import sys
sys.path.append('..')
import config
import util
import os

#选择所有score2 > 0 的用户
myCon = MySQLdb.connect(host=config.HOST, user='root', passwd=config.PASSWORD, db=config.DATABASE, charset='utf8')
sql = 'select * from nozomi_clan where score2 > 0 order by score2 desc limit 100'
myCon.query(sql)
res = myCon.store_result().fetch_row(0, 1)
num = 0
#reward = [10000, 5000, 3000, 100]
reward = [4, 3, 2, 1]
total = 0
totalc = 0
for i in res:
    cid = i["id"]
    sql = 'select id, lscore from nozomi_user where clan = %d' % (cid)
    myCon.query(sql)
    allUser = myCon.store_result().fetch_row(0, 1)
    rc = reward[min(len(reward)-1, num)]

    sql = 'select score2 from nozomi_clan where id = %d' % (cid)
    myCon.query(sql)
    res = myCon.store_result().fetch_row(0, 1)
    score2 = res[0]["score2"]
    nu = len(allUser)

    for u in allUser:
        sql = 'insert into nozomi_reward (uid, reward, remark, remark_cn) values(%d, %d, "%s", "%s")' % (u["id"], rc, "Your League get %d points, ranked %d, received %d crystals as total rewards\nYour Exploit is %d, get %d crystal as rewards" % (score2, num+1, rc*nu, u['lscore'], rc), "你的联盟获得了k1积分， 排名%d， 奖励%d水晶\n你的联盟功勋为k4,奖励水晶k5" % (num+1, rc))
        myCon.query(sql)
        total = total+1
        totalc = totalc+rc
    num = num+1

myCon.commit()
myCon.close()
print "total reward user", total, totalc
