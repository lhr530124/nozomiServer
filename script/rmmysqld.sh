mysql -uroot -pwavegame1 -e "PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 3 DAY);"
