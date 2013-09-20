#coding:utf8
from testConfig import *

baseScore = 'http://localhost:9958/'
r = baseScore+'updateScore?uid=1972&score=1162'
req(r)

#r = baseScore+'updateScore?uid=2&score=500'
#req(r)

#r = baseScore+'updateScore?uid=2&score=50'
#req(r)


r = baseScore+'getUserRank?uid=2&score=50' 
req(r)
