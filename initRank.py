#coding:utf8
#根据用户得分表 初始化用户排名表
from flaskext import *
myCon = getConn()

#删除旧的计数
sql = 'delete from nozomi_score_count'
myCon.query(sql)
myCon.commit()


sql = 'select * from nozomi_rank'
myCon.query(sql)
users = myCon.store_result().fetch_row(0, 1)
for i in users:
    sql = 'insert nozomi_score_count (`score`, `count`) values (%d, 1) on duplicate key update count = count+1 ' % (i['score'])
    myCon.query(sql)
    
myCon.commit()
myCon.close()
