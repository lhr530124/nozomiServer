import os
import time
now = time.localtime()
cur = time.strftime('%Y%m%d-%H%M%S', now)
os.system('mv /data/log/nginx/access.log /data/log/nginx/access.log-%s'%(cur))
os.system('mv /data/log/nginx/error.log /data/log/nginx/error.log-%s'%(cur))
os.system('kill -USR1 `cat /var/run/nginx.pid`')
os.system('sleep 1')
#os.system('gzip /data/log/nginx/access.log-%s'%(cur))
