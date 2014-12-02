# -*- coding: utf8 -*-
import time
import random
from flaskext import *
import sys
sys.path.append('..')
import config
import util

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
    rets = queryAll("SELECT `id`, score, lscore, name, memberType FROM `nozomi_user` WHERE clan=%s", (cid))
    return rets

def getClanInfo(cid):
    ret = queryOne("SELECT `id`, icon, score, `type`, name, `desc`, members, `min`, creator, state, statetime FROM `nozomi_clan` WHERE id=%s", (cid))
    return ret

def getTopClans():
    ret = queryAll("SELECT `id`, icon, score, `type`, name, `desc`, members, `min` FROM `nozomi_clan` WHERE members>0 ORDER BY score DESC LIMIT 50")
    return ret

def getTopClans2():
    ret = queryAll("SELECT `id`, icon, score2, `type`, name, `desc`, members, `min` FROM `nozomi_clan` WHERE members>0 ORDER BY score2 DESC LIMIT 50")
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
    if clan[9]<2:
        uinfo = queryOne("SELECT lscore, memberType FROM `nozomi_user` WHERE id=%s", (uid))
        lscore = uinfo[0]
        mtype = uinfo[1]
        clan[6] = clan[6]-1
        clan[2] = clan[2] - lscore
        update("UPDATE `nozomi_user` SET clan=0, lscore=0, memberType=0 WHERE id=%s", (uid))
        if mtype==2 and clan[6]>0:
            nuid = queryOne("SELECT id FROM `nozomi_user` WHERE clan=%s ORDER BY lscore DESC LIMIT 1", (cid))[0]
            update("UPDATE `nozomi_user` SET memberType=2 WHERE id=%s", (nuid))
        state = clan[9]
        if clan[6]==1:
            state = 0
        update("UPDATE `nozomi_clan` SET members=if(members>0,members-1,0), score=score-%s, state=%s WHERE id=%s", (lscore, state, cid))
        return clan
    return None
