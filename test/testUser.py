#coding:utf8
from testConfig import *
r = base2+'getBattleHistory?uid=4'
req(r)

r = base2+'findClans'
req(r)

r = base2+'login'
data = {'username':'liyong', 'nickname':'liyong'}
req2(r, data)

r = base2+'getData?uid=4'
req(r)

r = base2+'reverge?uid=4&eid=4'
req(r)

r = base2+'getReplay?vid=3'
req(r)

#level num achieves
r = base2+'synData'
data = {
'uid':1, 
'delete':json.dumps([0, 1, 2, 3]), 
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
'uid':10, 'eid':2,
'delete': json.dumps([1, 2, 3, 4]),
'update':json.dumps([[5, 4000, 10, 5, 5, 10, '']]), 
'hits': json.dumps([[5, 10]]),
'score': 20, 
'shieldTime': 1000,
'isReverge': True,
'history': 'xxx',
'replay': 'xxx',
}
req2(r, data)

r = base2+'findEnemy?uid=10&isGuide=1'
req(r)

r = base2+'findEnemy?uid=20'
req(r)

r = base2+'sendFeedback'
data = {
'uid': 2,
'text': 'good game',
}
req2(r, data)

r = baseScore+'updateScore?uid=2&score=10'
req(r)

r = baseScore+'getUserRank?uid=2&score=20' 
req(r)

r = baseScore+'getUserRank?uid=2&score=20'
req(r)

