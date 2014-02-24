import os
import time
now = time.localtime()
ss = time.strftime('%Y-%m-%d-%H-%M-%S', now)
os.system('mv /data/log/redis/redis.log /data/log/redis/redis.log-%s'%(ss))
