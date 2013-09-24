#!/bin/bash
date_str=`date +%Y%m%d`
cd /data/backup
mysqldump -hlocalhost -uroot -p2e4n5k2w2x -R -E -e nozomi | gzip > nozomi_$date_str.sql.gz
