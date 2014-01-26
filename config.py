HOST = 'localhost'
DATABASE = 'nozomi'
DEBUG = True
PASSWORD = 'ideacome'
ADMINS = ['233242872@qq.com', 'caesars321@gmail.com', '21024851@qq.com']
HOSTPORT = 9973
SORTPORT = 9968
CHATPORT = 8005
CHATSERVER = 'http://localhost:%d/sys' % (CHATPORT)
REDIS_HOST = 'localhost'
LOG_HOST= 'localhost'
LOG_PORT = 9020


ERROR_SERVER = "nozomiTestError.log"
ERROR_RANK = "rankError.log"
STATISTIC_PORT = 9004

dbInfo = [
{'host':'localhost', 'user':'root', 'passwd':'ideacome', 'db':DATABASE}, 
{'host':'localhost', 'user':'root', 'passwd':'ideacome', 'db':DATABASE}, 
]
userCut = [1000000, 99999999]
