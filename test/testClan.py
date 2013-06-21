#coding:utf8
from testConfig import *
enemyId = 3
r = base2+'createClan'
data = {'uid':enemyId, 'icon':1, 'type':0, 'name':'wangguoqiji', 'desc':'battle for war', 'minScore':100}
l = req2(r, data)
enemyClan = l['clan']

uid = 2
r = base2+'createClan'
data = {'uid':uid, 'icon':1, 'type':0, 'name':'wangguoqiji', 'desc':'battle for war', 'minScore':100}
l = req2(r, data)
clanId = l['clan']

r = base2+'getClanMembers?cid=%d' % (clanId)
req(r)

r = base2+'getRandomClans?score=100'
req(r)

r = base2+'searchClans?word=wangguo'
req(r)

r = base2+'searchClans?word=liyong'
req(r)

r = base2+'findLeagueEnemy'
data = {"uid":uid, "cid":clanId, "score":100, "eid":enemyClan}
req2(r, data)

r = base2+'findLeagueEnemy'
data = {"uid":uid, "cid":clanId, "score":100}
req2(r, data)

r = base2+'cancelFindLeagueEnemy'
data = {"cid":clanId, "uid":uid }
req2(r, data)


#确保敌对联盟存在即可
r = base2+'beginLeagueBattle'
data = {'cid':clanId, 'eid':enemyClan, 'uid':uid}
req2(r, data)

r = base2+'leaveClan'
data = {'uid':uid, 'cid':clanId}
req2(r, data)

r = base2+'joinClan'
data = {'uid':uid, 'cid':clanId}
req2(r, data)

r = base2+'getLeagueBattleInfo?cid=%d' % (clanId)
req(r)

r = base2+'getLeagueMemberData?uid=%d&euid=%d' % (uid, 3)
req(r)

r = base2+'clearBattleState'
data = {'eid':enemyClan}
req2(r, data)

r = base2+'getLeagueRank'
req(r)



