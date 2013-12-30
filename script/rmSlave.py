import os
import time
now = time.time()
#delete all 10days ago log files
now -= 24*3600*30
for i in xrange(20):
	startDay = time.localtime(now) 
	os.system('rm /data/backup/nozomi2_%d%02d%02d.sql.gz -f'%(startDay.tm_year, startDay.tm_mon, startDay.tm_mday))
	os.system('rm /data/backup/nozomi_%d%02d%02d.sql.gz -f'%(startDay.tm_year, startDay.tm_mon, startDay.tm_mday))
	print "remove", startDay
	now = now+24*3600

