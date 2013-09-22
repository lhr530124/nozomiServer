import MySQLdb
import urllib
import json
import sys
import random
import time
import urllib2
import sys
sys.path.append('..')
import config
#myCon = MySQLdb.connect(host='uhz000738.chinaw3.com', passwd='2e4n5k2w2x', db='nozomi', user='root', charset='utf8')

#myCon = MySQLdb.connect(host='localhost', passwd='wavegame1', db='nozomiTest', user='root', charset='utf8')

base2 = 'http://localhost:%d/' % (config.HOSTPORT)
baseScore = 'http://localhost:%d/' % (config.SORTPORT)

def exe(sql):
    print sql
    con.query(sql)
    return con.store_result()

def req(r):
    print r
    q = urllib.urlopen(r)
    s = q.read()
    l = None
    try:
        l = json.loads(s)
        print l
    except:
        print "error\n"
        sys.stderr.write(r+'\n'+s+'\n')
    return l

def req2(r, data):
    print r
    print data
    print urllib.urlencode(data)

    q = urllib2.urlopen(r, urllib.urlencode(data))
    s = q.read()
    l = None
    try:
        l = json.loads(s)
        print l
    except:
        print "error\n"
        sys.stderr.write(r+'\n'+s+'\n')
    return l

