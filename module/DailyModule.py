from flaskext import *
import time, datetime
class DailyModule:

    def __init__(self, dbname):
        self.selectSql = "SELECT loginDays, loginDate FROM " + dbname + " WHERE uid=%s"
        self.updateSql = "INSERT INTO " + dbname + " (uid, loginDays, loginDate) VALUES (%s,%s,%s) ON DUPLICATE KEY UPDATE loginDays=VALUES(loginDays),loginDate=VALUES(loginDate)"

    def dailyLogin(self, uid):
        ret = queryOne(self.selectSql, (uid))
        today = datetime.date.today()
        days = 1
        if ret!=None:
            timedelta = (today - ret[1]).days
            if timedelta==0:
                days = 0
            elif timedelta==1:
                days = ret[0]+1
        if days>0:
            update(self.updateSql, (uid, days, today))
        return days
        
