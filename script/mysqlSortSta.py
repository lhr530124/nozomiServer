#coding:utf8
import sys
sys.path.append('..')
import config
import MySQLdb

con = MySQLdb.connect(host='localhost', db='nozomi', user='root', passwd=config.PASSWORD)
sql = 'show tables '
con.query(sql)
res = con.store_result().fetch_row(0, 0)
tables = set()
for r in res:
    tables.add(r[0])

f = open('../mysqlSortLog.log')
#统计每个请求的时间
#tableNames 

kinds = {}
#statics = {}

for l in f.readlines():
    l = l.split('\t')
    if len(l) >= 2:
        k = None
        if l[0].find('SELECT')  != -1:
            k = 'SELECT'
        elif l[0].find('UPDATE') != -1:
            k = 'UPDATE'
        elif l[0].find('INSERT') != -1:
            k = 'INSERT'
        elif l[0].find('DELETE') != -1:
            k = 'DELETE'
            
        if k != None:
            vv = kinds.setdefault(k, {})

            for db in tables:
                if l[0].find(db) != -1:
                    v = vv.setdefault(db, 0)
                    v += int(l[1])
                    vv[db] = v
                    break
def cmp(a, b):
    return b[1]-a[1]
            
for k, v in kinds.items():
    vv = v.items()
    vv.sort(cmp=cmp)
    print k
    print vv
