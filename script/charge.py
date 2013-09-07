import MySQLdb
import time
con = MySQLdb.connect(host='localhost', user='root', passwd='wavegame1', db='nozomi', charset='utf8')

sql = 'select id, name, lastSynTime, totalCrystal from nozomi_user where totalCrystal > 0'
con.query(sql)
res = con.store_result().fetch_row(0, 1)
now = int(time.time())
twoDay = []
threeDay = []
for i in res:
    if now - i['lastSynTime'] > 86400*3:
        twoDay.append(i)
    elif now -i['lastSynTime'] > 86400*2:
        threeDay.append(i)

print 'two'
for i in twoDay:
    print i['id'], i['name'], i['totalCrystal']

print 'three'
for i in threeDay:
    print i['id'], i['name'], i['totalCrystal']
        
        
