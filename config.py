HOST = '127.0.0.1'
DATABASE = 'nozomi'
DEBUG = False
PASSWORD = 'wavegame1'
ADMINS = ['21024851@qq.com']
HOSTPORT = 9995
SORTPORT = 9958
CHATPORT = 8005
CHATSERVER = 'http://127.0.0.1:%d/sys' % (CHATPORT)
REDIS_HOST = '127.0.0.1'
LOG_HOST= '127.0.0.1'
LOG_PORT = 9020


ERROR_SERVER = "nozomiTestError.log"
ERROR_RANK = "rankError.log"
STATISTIC_PORT = 9004

dbInfo = [
{'host':'127.0.0.1', 'user':'root', 'passwd':'wavegame1', 'db':DATABASE}, 
]
userCut = [1000000, 99999999]
