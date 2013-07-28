import time
beginTime = (2013, 1, 1, 0, 0, 0, 0, 0, 0)
beginTime = int(time.mktime(beginTime))
def getTime():
    return int(time.time()-beginTime)
