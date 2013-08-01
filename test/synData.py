
#coding:utf8
from testConfig import *

#base2 = "http://23.21.135.42:9927/"
#base2 = 'http://localhost:%d/' % (config.HOSTPORT)
r = base2+'synData'
testValue = (0, 99, 0, 500, 0, 27000, 0, 21000, 0, 5500, 0,  5600)
#testValue = (0, 99)
for v in testValue:
    data = {
    'uid':2, 
    'delete':json.dumps([]), 
    'update':json.dumps([]), 
    'achieves':json.dumps([]), 
    'userInfo':json.dumps({'crystal':v}),
    'research':json.dumps([1, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
    #'crystal':json.dumps([[1, 1989, 0]]),
    'eid':1,
    }
    req2(r, data)

