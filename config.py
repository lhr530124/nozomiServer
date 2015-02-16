HOST = '10.68.55.40'
DATABASE = 'nozomi'
DEBUG = False
PASSWORD = 'wavegame1'
ADMINS = ['21024851@qq.com']
HOSTPORT = 9995
SORTPORT = 9958
CHATPORT = 8005
CHATSERVER = 'http://10.68.55.40:%d/sys' % (CHATPORT)
REDIS_HOST = '10.68.55.40'
LOG_HOST= '10.68.55.40'
LOG_PORT = 9020


ERROR_SERVER = "nozomiTestError.log"
ERROR_RANK = "rankError.log"
STATISTIC_PORT = 9004

dbInfo = [
{'host':'10.68.55.40', 'user':'root', 'passwd':'wavegame1', 'db':DATABASE}, 
{'host':'10.151.82.234', 'user':'root', 'passwd':'wavegame1', 'db':'nozomi2'}, 
{'host':'10.68.55.40', 'user':'root', 'passwd':'wavegame1', 'db':DATABASE, 'port':3307}, 
]
userCut = [1000000, 99999999]
