import os
import time
now = time.time()
now -= 24*3600*45
now = time.localtime(now)
os.system('rm /data/log/mysqld.log-%d-%d-* -f'%(now.tm_year, now.tm_mon))
os.system('rm /data/log/redis.log-%d-%d-* -f'%(now.tm_year, now.tm_mon))
os.system('rm /data/nozomi-9-24-logServer/allLog/*.%d-%d-* -f'%(now.tm_year, now.tm_mon))
