#coding:utf8
from testConfig import *
r = base2+'checkKeyWord?'+urllib.urlencode({'word':"fuck fuck you"})
req(r)

r = base2+'checkKeyWord?'+urllib.urlencode({'word':"中国人民大团结万岁"})
req(r)

r = base2+'blockWord?'+urllib.urlencode({'word':'fuck fuck you'})
req(r)

r = base2+'blockWord?'+urllib.urlencode({'word':"中国人民大团结万岁"})
req(r)

