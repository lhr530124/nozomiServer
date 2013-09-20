#coding:utf8
import urllib2
import urllib
import sys
import json

def req(r):
    print r
    q = urllib.urlopen(r)
    s = q.read()
    l = None
    try:
        l = json.loads(s)
        #print l
    except:
        #print "error\n"
        sys.stderr.write(r+'\n'+s+'\n')
    return l

baseurl = 'http://23.21.135.42:8006/'
r = baseurl+'send?'
data = {
'uid':123,
'name':'xiaoming',
'cid':1,
'text':'wolai le~~',
}
r += urllib.urlencode(data)
req(r)


r = baseurl+'recv?'
data = {
'uid':2,
'cid':1,
'since':0,
}
r += urllib.urlencode(data)
req(r)

r = baseurl+'send?'
data = {
'uid':234,
'name':'wangge',
'cid':2,
'text':'wange ge zai 2',
}
r += urllib.urlencode(data)
req(r)


r = baseurl+'recv?'
data = {
'uid':2,
'cid':2,
'since':0,
}
r += urllib.urlencode(data)
req(r)


#重启聊天服务器 check 恢复 数据是否正确

"""
r = baseurl+'send?'

for i in xrange(0, 101):
    data = {
    'uid':234,
    'name':'wangge',
    'cid':3,
    'text':'wange ge zai '+str(i),
    }
    m = r + urllib.urlencode(data)
    req(m)
"""

    
r = baseurl+'recv?'
data = {
'uid':2,
'cid':3,
'since':0,
}
r += urllib.urlencode(data)
l = req(r)
print len(l['messages'])


#请求空白的聊天室


r = baseurl+'sys?'
data = {
'uid':2,
'type':'join',
'info':'dream',
'cid':3,
}
r += urllib.urlencode(data)
req(r)


r = baseurl+'request?'
data = {
'uid':2,
'name':'liyongh',
'cid':3,
'space':2,
'max':10,
}
r += urllib.urlencode(data)
req(r)

r = baseurl+'donate?'
data = {
'uid':3,
'toUid':2,
'cid':3,
'sid':0,
'slevel':10,
'space':'1',
}

r += urllib.urlencode(data)
req(r)

r = baseurl+'recv?'
data = {
'uid':2,
'cid':3,
'since':0,
}
r += urllib.urlencode(data)
l = req(r)
print len(l['messages'])
