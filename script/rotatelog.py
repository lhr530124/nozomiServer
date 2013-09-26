import os
import time
now = time.localtime()
st = time.strftime('%Y-%m-%d-%H-%M-%S', now)
os.system('mv /data/log/mysqld.log /data/log/mysqld.log-%s' % (st))
os.system('mysqladmin -uroot -pwavegame1 flush-logs')
