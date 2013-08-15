#coding:utf8
from testConfig import *

#老数据库
r = base2+'getData?uid=2'
req(r)

#新数据库
r = base2+'login'
data = {'username':'liyongTest2', 'nickname':'liyongTest2'}
l = req2(r, data)
nuid = l['uid']

r = base2+'getData?uid=%d'%(nuid)
req(r)



r = base2+'synData'
data = {
'uid':2, 
'delete':json.dumps([2, 3]), 
'update':json.dumps([[1, 4000, 10, 5, 5, 10, '']]), 
'achieves':json.dumps([[10, 10, 0]]), 
'research':json.dumps([1, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
'userInfo':json.dumps({'shieldTime':10, 'guideValue':1400}),
'eid':1,
'stat': 'finidLog',
'crystal': json.dumps([1, 2, 3]),
}
req2(r, data)

r = base2+'synData'
data = {
'uid':nuid, 
'delete':json.dumps([2, 3]), 
'update':json.dumps([[1, 4000, 10, 5, 5, 10, '']]), 
'achieves':json.dumps([[10, 10, 0]]), 
'research':json.dumps([1, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
'userInfo':json.dumps({'shieldTime':10, 'guideValue':1400}),
'eid':1,
'stat': 'finidLog',
'crystal': json.dumps([1, 2, 3]),
}
req2(r, data)


r = base2+'synBattleData'
data = {
'uid':2, 'eid':2,
'eupdate':json.dumps([[4, 'testData']]), 
'hits': json.dumps([[5, 10]]),
'score': 20, 
'shieldTime': 1000,
'isReverge': True,
'history': 'xxx',
'replay': 'xxx',
}
req2(r, data)


r = base2+'synBattleData'
data = {
'uid':nuid, 'eid':2,
'eupdate':json.dumps([[4, 'testExtend']]), 
'hits': json.dumps([[5, 10]]),
'score': 20, 
'shieldTime': 1000,
'isReverge': True,
'history': 'xxx',
'replay': 'xxx',
}
req2(r, data)



