# -*- coding: utf8 -*-
import time
import random
from flaskext import *
import sys
sys.path.append('..')
import config


#clan's state 0 means free, 1 means wait to battle, 2 means in battle.

def getRandomClans(score):
    rets = queryAll("SELECT `id`,icon,score,`type`,name,`desc`,members, `min`, creator FROM `nozomi_clan` WHERE `min`<=%s AND members>0 AND members<50 LIMIT 50", (score))
    return rets

def searchClans(text):
    text = text.strip().replace("%","")
    if text=="":
        return None
    isUnicode = False
    for i in range(len(text)):
        if ord(text[i])>=128:
            if i==0:
                text = text[:3]
                isUnicode = True
            else:
                text = text[:i]
            break
    if isUnicode:
        return queryAll("SELECT `id`,icon,score,`type`,name,`desc`,members,`min`,creator FROM `nozomi_clan` WHERE `name` LIKE %s AND members>0 LIMIT 50", (text+"%"))
    rets = queryAll("SELECT `id`,icon,score,`type`,name,`desc`,members,`min`,creator FROM `nozomi_clan` WHERE MATCH(`name`) AGAINST (%s) AND members>0 LIMIT 50", (text))
    return rets

def createClan(uid, icon, ltype, name, desc, minScore):
    id = insertAndGetId("INSERT INTO `nozomi_clan` (icon, score, type, name, `desc`, members, `min`, creator, state, statetime) VALUES(%s,0,%s,%s,%s,1,%s,%s,0,0)", (icon, ltype, name, desc, minScore, uid))
    update("UPDATE `nozomi_user` SET clan=%s, memberType=2 WHERE id=%s", (id, uid))
    return id

def editClan(cid, icon, ltype, name, desc, minScore):
    update("UPDATE `nozomi_clan` SET icon=%s,type=%s,name=%s,`desc`=%s,`min`=%s WHERE id=%s", (icon,ltype,name,desc,minScore,cid))
    return 0

def getClanMembers(cid):
    rets = queryAll("SELECT `id`, score, lscore, name, memberType FROM `nozomi_user` WHERE clan=%s ORDER BY score DESC", (cid))
    return rets

def getClanInfo(cid):
    ret = queryOne("SELECT `id`, icon, score, `type`, name, `desc`, members, `min`, creator, state, statetime FROM `nozomi_clan` WHERE id=%s", (cid))
    if ret!=None and ret[9]==2:
        curTime = int(time.mktime(time.localtime()))
        if curTime>ret[10]:
            #compute winner
            binfo = queryOne("SELECT id, cid1, cid2, left1, left2 FROM `nozomi_clan_battle` WHERE winner=0 AND (cid1=%s OR cid2=%s)", (cid, cid))
            winner = 1
            if binfo[4]>binfo[3]:
                winner = 2
            update("UPDATE `nozomi_clan_battle` SET winner=%s WHERE id=%s", (winner, binfo[0]))
            update("UPDATE `nozomi_clan` SET state=0, statetime=0 WHERE id=%s", (binfo[3-winner]))
            update("UPDATE `nozomi_clan` SET state=0, statetime=0, score=score+30 WHERE id=%s", (binfo[winner]))
            params = []
            m1 = sorted(getClanMembers(binfo[1]), key=lambda x:x[2], reverse=True)
            m2 = sorted(getClanMembers(binfo[2]), key=lambda x:x[2], reverse=True)
            ednum = 9
            for m in m1:
                if m[4]==2:
                    continue
                mtype = 0
                if ednum>0:
                    ednum=ednum-1
                    mtype=1
                if mtype!=m[4]:
                    params.append([mtype, m[0]])
            ednum = 9
            for m in m2:
                if m[4]==2:
                    continue
                mtype = 0
                if ednum>0:
                    ednum=ednum-1
                    mtype=1
                if mtype!=m[4]:
                    params.append([mtype, m[0]])
            executemany("UPDATE `nozomi_user` SET memberType=%s WHERE id=%s", params)
            #"http://uhz000738.chinaw3.com:8004/sys"
            #"http://uhz000738.chinaw3.com:8004/sys"
            requestGet(config.CHATSERVER, dict(cid=binfo[1], type="lbe", info=binfo[winner]))
            requestGet(config.CHATSERVER , dict(cid=binfo[2], type="lbe", info=binfo[winner]))
            ret = list(ret)
            ret[9]=0
            ret[10]=0
    return ret

def getTopClans():
    ret = queryAll("SELECT `id`, icon, score, `type`, name, `desc`, members, `min` FROM `nozomi_clan` WHERE members>0 ORDER BY score DESC LIMIT 50")
    return ret

def joinClan(uid, cid):
    clan = list(getClanInfo(cid))
    if clan[6]<50 and clan[9]<2:
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
        update("UPDATE `nozomi_clan` SET members=members-1, score=score-%s, state=%s WHERE id=%s", (lscore, state, cid))
        return clan
    return None

def resetClanState(cid, state):
    update("UPDATE `nozomi_clan` SET state=%s, statetime=0 WHERE id=%s", (state, cid))

def checkFindLeagueAuth(uid, cid):
    print("check auth param %d, %d" % (uid, cid))
    uinfo = queryOne("SELECT clan, memberType FROM `nozomi_user` WHERE id=%s", (uid))
    if uinfo[0]==cid and uinfo[1]>0:
        return True
    return False

def findLeagueEnemy(cid, score):
    curTime = int(time.mktime(time.localtime()))
    scoreOff = 500
    while scoreOff<1000:
        minScore = score-scoreOff
        maxScore = score+scoreOff

        ids = queryOne("SELECT MIN(id), MAX(id) FROM `nozomi_clan` WHERE score>%s AND score<%s AND state=1 AND members>0", (minScore, maxScore))
        if ids!=None:
            minId = ids[0]
            maxId = ids[1]
            if maxId != None and minId!=None:
                cut = random.randint(minId, maxId)
                ret = queryOne("SELECT id,icon,score,`type`,name,`desc`,members FROM `nozomi_clan` WHERE id>=%s AND id!=%s AND state=1 AND statetime<%s AND score>%s AND score<%s AND members>0 LIMIT 1", (cut, cid, curTime, minScore, maxScore))
                if ret!=None:
                    print("find league enemy %d" % ret[0])
                    update("UPDATE `nozomi_clan` SET statetime=%s WHERE id=%s", (curTime+180, ret[0]))
                    members = getClanMembers(ret[0])
                    ret = list(ret)
                    ret.append(members)
                    return ret
        scoreOff *= 2
    resetClanState(cid, 1)
    return [0]

def cancelFindLeagueEnemy(cid):
    info = getClanInfo(cid)
    if info[9]==1:
        resetClanState(cid, 0)
        return 0
    else:
        return 1

def beginLeagueBattle(cid, eid):
    info = getClanInfo(eid)
    curTime = int(time.mktime(time.localtime()))
    if info[9]==1 and info[10]>curTime and info[6]>0:
        update("UPDATE `nozomi_clan` SET state=2, statetime=%s WHERE id=%s OR id=%s", (curTime+86400, cid, eid))
        cinfo = getClanInfo(cid)
        bid = insertAndGetId("INSERT INTO `nozomi_clan_battle` (cid1, cid2, left1, left2, winner) VALUES (%s,%s,%s,%s,0)", (cid, eid, cinfo[6], info[6]))
        members = []
        cmems = getClanMembers(cid)
        for mem in cmems:
            members.append([mem[0], bid, cid])
        emems = getClanMembers(eid)
        for mem in emems:
            members.append([mem[0], bid, eid])
        executemany("INSERT INTO `nozomi_clan_battle_member` (uid, bid, cid, battler, video, inbattle) VALUES (%s,%s,%s,'',0,0) ON DUPLICATE KEY UPDATE bid=VALUES(bid), cid=VALUES(cid), battler='', video=0, inbattle=0", members)
        requestGet(config.CHATSERVER, dict(cid=cid, type="lbb", info=curTime+86400))
        requestGet(config.CHATSERVER, dict(cid=eid, type="lbb", info=curTime+86400))
        return 0
    return 1

def getLeagueBattleInfo(cid):
    battle = queryOne("SELECT id, cid1, cid2, left1, left2 FROM `nozomi_clan_battle` WHERE winner=0 AND (cid1=%s OR cid2=%s)", (cid, cid))
    if battle==None:
        return None
    members = queryAll("SELECT uid, cid, battler, video, inbattle FROM `nozomi_clan_battle_member` WHERE bid=%s", (battle[0]))
    battle=list(battle)
    battle.append(members)
    return battle

def clearBattleStateAtOnce(uid):
    update("UPDATE `nozomi_clan_battle_member` SET inbattle=0, battler='' WHERE uid=%s", (uid))

def checkBattleWithMember(uid, euid):
    battleMember = queryOne("SELECT uid, bid, video, inbattle, battler FROM `nozomi_clan_battle_member` WHERE uid=%s", (euid))
    selfMember = queryOne("SELECT uid, bid, video, inbattle, battler FROM `nozomi_clan_battle_member` WHERE uid=%s", (uid))
    if battleMember==None or selfMember==None:
        return 1
    if battleMember[2]>0:
        return 2
    curTime = int(time.mktime(time.localtime()))
    # this means the battler lose his connection when attacking
    if battleMember[3]>curTime and int(battleMember[4])!=uid:
        return 1
    if selfMember[3]>curTime:
        return 3
    update("UPDATE `nozomi_clan_battle_member` SET inbattle=%s, battler=%s WHERE uid=%s", (curTime+240, str(uid), euid))
    return 0

def changeBattleState(uid, eid, cid, ecid, bid, vid, lscore):
    print("test change %d,%d,%d,%d,%d,%d,%d" % (uid, eid, cid, ecid, bid, vid, lscore))
    if lscore>0:
        update("UPDATE `nozomi_user` SET lscore=lscore+%s WHERE id=%s", (lscore, uid))
        binfo = queryOne("SELECT id, cid1, cid2, left1, left2, winner FROM `nozomi_clan_battle` WHERE id=%s", (bid))
        
        if binfo[5]==0:
            winner = 0
            isE1 = (binfo[1]==ecid)
            eleftIndex = 4
            if isE1:
                eleftIndex = 3
            if binfo[eleftIndex]==1:
                lscore = lscore+30
                winner = 5-eleftIndex
                update("UPDATE `nozomi_clan` SET state=0, statetime=0 WHERE id=%s or id=%s", (cid, ecid))
                params = []
                m1 = sorted(getClanMembers(cid), key=lambda x:x[2], reverse=True)
                m2 = sorted(getClanMembers(ecid), key=lambda x:x[2], reverse=True)
                ednum = 9
                for m in m1:
                    if m[4]==2:
                        continue
                    mtype = 0
                    if ednum>0:
                        ednum=ednum-1
                        mtype=1
                    if mtype!=m[4]:
                        params.append([mtype, m[0]])
                ednum = 9
                for m in m2:
                    if m[4]==2:
                        continue
                    mtype = 0
                    if ednum>0:
                        ednum=ednum-1
                        mtype=1
                    if mtype!=m[4]:
                        params.append([mtype, m[0]])
                executemany("UPDATE `nozomi_user` SET memberType=%s WHERE id=%s", params)
                
                requestGet(config.CHATSERVER, dict(cid=cid, type="lbe", info=cid))
                requestGet(config.CHATSERVER, dict(cid=ecid, type="lbe", info=cid))
            if isE1:
                update("UPDATE `nozomi_clan_battle` SET left1=left1-1, winner=%s WHERE id=%s", (winner, bid))
            else:
                update("UPDATE `nozomi_clan_battle` SET left2=left2-1, winner=%s WHERE id=%s", (winner, bid))
        update("UPDATE `nozomi_clan` SET score=score+%s WHERE id=%s", (lscore, cid))
        name = queryOne("SELECT name FROM `nozomi_user` WHERE id=%s", (uid))[0]
        update("UPDATE `nozomi_clan_battle_member` SET inbattle=0, battler=%s, video=%s WHERE uid=%s", (name, vid, eid))
    else:
        clearBattleStateAtOnce(eid)
    #    update("UPDATE `nozomi_user` SET lscore=lscore+%s WHERE id=%s", (-lscore, eid))
    #    update("UPDATE `nozomi_clan` SET score=score+%s WHERE id=%s", (-lscore, ecid))
