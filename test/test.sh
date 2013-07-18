#ab -n 1000 -c 100 http://localhost:9003/getData?uid=29
#ab -n 1000 -c 100 -p de.txt http://localhost:9003/synData
#ab -n 1000 -c 100 -p up.txt -T "application/x-www-form-urlencoded" http://localhost:9003/synData
#ab -n 1000 -c 100 -p hit.txt -T "application/x-www-form-urlencoded" http://localhost:9003/synData
#ab -n 1000 -c 100 http://localhost:9003/findEnemy?uid=20
#ab -n 1000 -c 100 -p sen.txt http://localhost:9003/sendFeedBack
#ab -n 1000 -c 100 http://localhost:9003/getReplay?vid=2
#ab -n 1000 -c 100 http://localhost:9002/getUserRank?uid=2\&score=500
#ab -n 1000 -c 100 http://localhost:9002/updateScore?uid=2\&score=100


ab -n 1000 -c 100 -p create.txt http://localhost:9003/createClan
ab -n 1000 -c 100 http://localhost:9003/getClanMembers?cid=11 
ab -n 1000 -c 100 http://localhost:9003/getRandomClans?score=100
ab -n 1000 -c 100 http://localhost:9003/searchClans?word=wangguo
ab -n 1000 -c 100 -p find.txt  http://localhost:9003/findLeagueEnemy
ab -n 1000 -c 100 -p can.txt  http://localhost:9003/cancelFindLeagueEnemy
ab -n 1000 -c 100 -p begin.txt  http://localhost:9003/beginLeagueBattle
ab -n 1000 -c 100 -p leave.txt  http://localhost:9003/leaveClan
ab -n 1000 -c 100 -p join.txt  http://localhost:9003/joinClan

#需要在nozomi_clan_battle 里面将winner 设定为 0 
ab -n 1000 -c 100  http://localhost:9003/getLeagueBattleInfo?cid=3
ab -n 1000 -c 100  http://localhost:9003/getLeagueMemberData?uid=2\&eid=3
ab -n 1000 -c 100 -p clear.txt  http://localhost:9003/clearBattleState
ab -n 1000 -c 100  http://localhost:9003/getLeagueRank









