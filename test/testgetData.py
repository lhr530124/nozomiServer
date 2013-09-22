
#coding:utf8
from testConfig import *

r = base2+'getData?uid=3&version=1&check=1&checkVersion=1&login=1'
req(r)


r = base2+'getData?uid=3&version=1&login=1'
req(r)

#r = base2+'getData?uid=2&version=3'
#req(r)

r = base2+'login'
data = {'username':'liyonggetdata', 'nickname':'liyong'}
l = req2(r, data)
uid = l['uid']

r = base2+'getData?uid=%d&login=1' % (uid)
req(r)
