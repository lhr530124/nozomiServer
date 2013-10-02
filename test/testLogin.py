#coding:utf8
from testConfig import *
r = 'http://localhost:9995/'+'login'
data = {'username':'liyongtestlog', 'nickname':'liyong'}
#for i in xrange(0, 100000):
#i = 0
#data = {
#'username': 'TEST%d' % (i),
#'nickname': 'TEST%d' % (i),
#}
req2(r, data)
#没有这个建筑 有 科研建筑

r = base2+'synData'
data = {
'uid':2, 
'update':json.dumps([[100, 100, 1002, 5, 5, 10, '']]), 
'research':json.dumps([1, 2, 2, 2, 2, 2, 2, 2, 2, 2]),
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

