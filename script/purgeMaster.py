import os
import time
import MySQLdb
con = MySQLdb.connect(host='localhost', db='nozomi', user='root', passwd='wavegame1')
sql = 'show master logs'
con.query(sql)
logs = con.store_result().fetch_row(0, 0)
print logs
if len(logs) > 3:
    sql = 'purge master logs to '+logs[-3][0]
    con.query(sql)

