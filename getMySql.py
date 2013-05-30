import os
import time
now = int(time.time())
os.system('mysqldump -uroot -p2e4n5k2w2x -h uhz000738.chinaw3.com nozomi > nozomi.sql')
os.system('mysql nozomi -uroot -pbadperson3 -A < nozomi.sql > nozomi.log')
