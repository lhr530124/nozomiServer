#coding:utf8
from testConfig import *

r = base2+'login'
for i in xrange(5000, 100000):
#i = 1000
    data = {
    'username': 'TEST%d' % (i),
    'nickname': 'TEST%d' % (i),
    }
    req2(r, data)

"""
r = base2+'getData?uid=3'
req(r)
"""


#同步200个建筑物信息
#删除 
#更新建筑物
#

"""
r = base2+'synData'
up = []
for i in xrange(1, 200):
    up.append({'buildIndex':i, 'grid':4000, 'bid':10, 'level':5, 'time':5, 'hitpoints':10})

data = {
'uid':1, 
'delete':json.dumps([0, 1, 2, 3]), 
'update':json.dumps(up), 
'achieves':json.dumps([[10, 10, 0]]), 
'research':json.dumps([1, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
'userInfo':json.dumps({'shieldTime':10, 'guideValue':1400}),
'eid':1,
'stat': 'finidLog',
'crystal': json.dumps([1, 2, 3]),
}
req2(r, data)
"""
