import os
import time
now = time.localtime()
ss = time.strftime('%Y-%m-%d-%H-%M-%S', now)
os.system('mv /data/log/redis.log /data/log/redis.log-%s'%(ss))
