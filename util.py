import time
beginTime = (2013, 1, 1, 0, 0, 0, 0, 0, 0)
beginTime = int(time.mktime(beginTime))
def getTime():
    return int(time.time()-beginTime)

def getToday():
    nt = time.localtime()
    today = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 ))
    return today-beginTime

def getYesterday():
    nt = time.localtime()
    yesterday = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday-1, 0, 0, 0, 0, 0, 0 ))
    return yesterday-beginTime

def getAbsToday():
    nt = time.localtime()
    today = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday, 0, 0, 0, 0, 0, 0 ))
    return today

def getAbsYesterday():
    nt = time.localtime()
    yesterday = time.mktime((nt.tm_year, nt.tm_mon, nt.tm_mday-1, 0, 0, 0, 0, 0, 0 ))
    return yesterday
