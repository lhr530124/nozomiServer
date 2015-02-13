# -*- coding: utf8 -*-
import time
import random
from flaskext import *
import sys
sys.path.append('..')
import config
import util
import json
#clan's state 0 means free, 1 means wait to battle, 2 means in battle.

def getRandomClans(score):
    rets = queryAll("SELECT `id`,icon,score,`type`,name,`desc`,members, `min`, creator FROM `nozomi_clan` WHERE `min`<=%s AND members>=4 AND members<10 LIMIT 50", (score))
    return rets

def searchClans(text):
    text = text.strip().replace("%","")
    if text=="":
        return None
    return queryAll("SELECT `id`,icon,score,`type`,name,`desc`,members,`min`,creator FROM `nozomi_clan` WHERE `name` LIKE %s AND members>0 LIMIT 50", (text+"%"))

def createClan(uid, icon, ltype, name, desc, minScore):
    id = insertAndGetId("INSERT INTO `nozomi_clan` (icon, score, type, name, `desc`, members, `min`, creator, state, statetime) VALUES(%s,0,%s,%s,%s,1,%s,%s,0,0)", (icon, ltype, name, desc, minScore, uid))
    update("UPDATE `nozomi_user` SET clan=%s, memberType=2 WHERE id=%s", (id, uid))
    return id

def editClan(cid, icon, ltype, name, desc, minScore):
    update("UPDATE `nozomi_clan` SET icon=%s,type=%s,name=%s,`desc`=%s,`min`=%s WHERE id=%s", (icon,ltype,name,desc,minScore,cid))
    return 0

def getClanMembers(cid):
    rets = queryAll("SELECT `id`, score, lscore, name, memberType, level, totalCrystal, uglevel, dnum, rdnum FROM `nozomi_user` WHERE clan=%s", (cid))
    return rets

def getClanInfo(cid):
    ret = queryOne("SELECT `id`, icon, score, `type`, name, `desc`, members, `min`, creator, state, statetime FROM `nozomi_clan` WHERE id=%s", (cid))
    return ret

def getTopClans():
    ret = queryAll("SELECT `id`, icon, score, `type`, name, `desc`, members, `min` FROM `nozomi_clan` WHERE members>0 ORDER BY score DESC LIMIT 50")
    if ret==None:
        ret= []
    return ret

def getTopClans2():
    ret = queryAll("SELECT `id`, icon, score2, `type`, name, `desc`, members, `min` FROM `nozomi_clan` WHERE members>0 ORDER BY score2 DESC LIMIT 50")
    if ret==None:
        ret = []
    return ret

def joinClan(uid, cid):
    clan = list(getClanInfo(cid))
    user = queryOne("SELECT score FROM nozomi_user WHERE id=%s",(uid,))
    if clan[6]<50 and clan[9]<2:
        if clan[7]>user[0]+100:
            update("UPDATE `nozomi_user` SET ban=2 WHERE id=%s",(uid,))
            return None
        clan[6] = clan[6]+1
        update("UPDATE `nozomi_user` SET clan=%s, memberType=0 WHERE id=%s", (cid, uid))
        update("UPDATE `nozomi_clan` SET members=members+1 WHERE id=%s", (cid))
        return clan
    return None

def leaveClan(uid, cid):
    clan = list(getClanInfo(cid))
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT state,battlers FROM nozomi_arena_prepare WHERE id=%s AND atype=1",(cid,))
    cbinfo = cur.fetchone()
    if cbinfo!=None:
        if (cbinfo[0]==1 or cbinfo[1]=="") and clan[6]<5:
            cur.close()
            return None
        elif cbinfo[0]==2 and cbinfo[1]!="":
            battlers = json.loads(cbinfo[1])
            if uid in battlers:
                cur.close()
                return None
    cur.execute("SELECT lscore, memberType, clan FROM `nozomi_user` WHERE id=%s", (uid,))
    uinfo = cur.fetchone()
    lscore = uinfo[0]
    mtype = uinfo[1]
    if clan[6]>0:
        clan[6] = clan[6]-1
    clan[2] = clan[2] - lscore
    if clan[2]<0:
        clan[2] = 0
    if mtype==2 and clan[6]>0:
        cur.execute("SELECT id FROM `nozomi_user` WHERE clan=%s AND id!=%s ORDER BY memberType,lscore DESC LIMIT 1", (cid,uid))
        nuid = cur.fetchone()[0]
        cur.execute("UPDATE nozomi_user SET memberType=%s WHERE id=%s", (2, nuid))
    cur.execute("UPDATE nozomi_user SET clan=0, lscore=0, memberType=0 WHERE id=%s", (uid,))
    cur.execute("UPDATE `nozomi_clan` SET members=if(members>0,members-1,0), score=if(score>%s,score-%s,0) WHERE id=%s", (lscore, lscore, cid))
    cur.execute("DELETE FROM nozomi_league_boss_member WHERE id=%s",(uid,))
    con.commit()
    cur.close()
    return clan

def modifyMemberType(uid, targetUid, memberType):
    con = getConn()
    cur = con.cursor()
    cur.execute("SELECT memberType,clan FROM `nozomi_user` WHERE id=%s", (uid,))
    uinfo = cur.fetchone()
    error = 0
    if uinfo==None:
        error = 2
    elif uinfo[0]<=1 or (memberType>=2 and uinfo[0]!=2):
        error = 1
    else:
        cur.execute("SELECT memberType,clan FROM `nozomi_user` WHERE id=%s", (targetUid,))
        tinfo = cur.fetchone()
        if tinfo==None:
            error = 2
        elif tinfo[0]==2 or (tinfo[0]==3 and uinfo[0]!=2) or (tinfo[0]==1 and uinfo[0]<2):
            error = 1
        elif tinfo[0]==memberType or tinfo[1]!=uinfo[1]:
            error = 2
        else:
            cur.execute("UPDATE nozomi_user SET memberType=%s WHERE id=%s",(memberType, targetUid))
            if memberType==2:
                cur.execute("UPDATE nozomi_user SET memberType=%s WHERE id=%s",(3, uid))
            con.commit()
    cur.close()
    return error
