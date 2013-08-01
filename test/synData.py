
#coding:utf8
from testConfig import *

base2 = "http://23.21.135.42:9927/"
r = base2+'synData'
data = {
'uid':2, 
'delete':json.dumps([]), 
'update':json.dumps([]), 
'achieves':json.dumps([]), 
'userInfo':json.dumps({'crystal':5000}),
'research':json.dumps([1, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
'crystal':json.dumps([[1, 1989, 100]]),
'eid':1,
}
req2(r, data)
