import os
import time
now = time.time()
now -= 24*3600*30
for i in xrange(20):
    startDay = time.localtime(now)
    #os.system('rm /data/log/mysqld.log-%d-%02d-%02d* -f'%(startDay.tm_year, startDay.tm_mon, startDay.tm_mday))
    #os.system('rm /data/log/redis.log-%d-%02d-%02d* -f'%(startDay.tm_year, startDay.tm_mon, startDay.tm_mday))
    os.system('rm /data/nozomiServer/allLog/*.%d-%02d-%02d* -f'%(startDay.tm_year, startDay.tm_mon, startDay.tm_mday))
    print startDay
    now = now + 24*3600
