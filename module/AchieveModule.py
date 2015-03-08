from flaskext import *
class AchieveModule:

    def __init__(self, dbname):
        self.selectSql = "SELECT achieve, level, num FROM " + dbname + " WHERE uid=%s"
        self.initSql = "INSERT IGNORE INTO " + dbname + " (uid, achieve, level, num) VALUES (%s,%s,1,0)"
        self.updateSql = "UPDATE " + dbname + " SET level=%s, num=%s WHERE uid=%s AND achieve=%s"

    def getAchieves(self, uid):
        ret = queryAll(self.selectSql, (uid), 3)
        return ret

    def initAchieves(self, uid):
        params = []
        for i in range(1, 23):
            params.append([uid, i])
        executemany(self.initSql, params, 3)

    def updateAchieves(self, uid, params):
        nparams = []
        for p in params:
            nparams.append([p[1], p[2], uid, p[0]])
        executemany(self.updateSql, nparams, 3)
