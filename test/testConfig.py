import MySQLdb
import urllib
import json
import sys
import random
import time
import urllib2

base2 = 'http://localhost:9003/'
baseScore = 'http://localhost:9002/'

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

