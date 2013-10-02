#!/bin/bash
date_str=`date +%Y%m%d`
cd /data/backup
mysqldump -hlocalhost -uroot -pwavegame1 -R -E -e nozomi | gzip > nozomi_$date_str.sql.gz
mysqldump -hlocalhost -uroot -pwavegame1 -R -E -e nozomi2 | gzip > nozomi2_$date_str.sql.gz
