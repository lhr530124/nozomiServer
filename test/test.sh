ab -n 1000 -c 100 http://localhost:9000/getData?uid=29
ab -n 1000 -c 100 -p de.txt http://localhost:9000/synData
ab -n 1000 -c 100 -p up.txt -T "application/x-www-form-urlencoded" http://localhost:9000/synData
ab -n 1000 -c 100 -p hit.txt -T "application/x-www-form-urlencoded" http://localhost:9000/synData
ab -n 1000 -c 100 http://localhost:9000/findEnemy?uid=20
ab -n 1000 -c 100 -p sen.txt http://localhost:9000/sendFeedBack
ab -n 1000 -c 100 http://localhost:9000/getReplay?vid=2
ab -n 1000 -c 100 http://localhost:9002/getUserRank?uid=29&score=500
ab -n 1000 -c 100 http://localhost:9002/updateScore?uid=2&score=10
