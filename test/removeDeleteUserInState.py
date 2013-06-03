import MySQLdb
myCon = MySQLdb.connect(host='localhost', db='nozomi', passwd='2e4n5k2w2x', user='root', charset='utf8')
sql = 'delete from nozomi_user_state where `uid` not in (select `id` from nozomi_user);'
print sql
myCon.query(sql)
myCon.commit()
myCon.close()
