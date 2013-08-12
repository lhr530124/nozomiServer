#coding:utf8
from testConfig import *

baseScore = 'http://23.21.135.42:9938/'
r = baseScore+'updateScore?uid=2&score=10'
req(r)

r = baseScore+'updateScore?uid=2&score=50'
req(r)


r = baseScore+'getUserRank?uid=2&score=50' 
req(r)
