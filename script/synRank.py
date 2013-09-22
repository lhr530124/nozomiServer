import MySQLdb
<<<<<<< HEAD
con = MySQLdb.connect(host='localhost', passwd='2e4n5k2w2x', db='nozomi', user='root', charset='utf8')
=======
con = MySQLdb.connect(host='localhost', passwd='wavegame1', db='nozomi', user='root', charset='utf8')
>>>>>>> 2f0e93b1c31271499dbb6412e9628ebd859dd769
sql = 'select id, score from nozomi_user'
con.query(sql)
res = con.store_result().fetch_row(0, 1)
for i in res:
    sql = 'update nozomi_user_state set score = %d where uid = %d' % (i['score'], i['id'])
    con.query(sql)
    sql = 'update nozomi_rank set score = %d where uid = %d' % (i['score'], i['id'])
    con.query(sql)
con.commit()
con.close()
