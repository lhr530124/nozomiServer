#!/bin/bash
date_str=`date +%Y%m%d`
cd /backup
mysqldump -hlocalhost -uroot -pwavegame1 -l -F -R -E -e --max-allowed-packet=1048576 --net_buffer_length=16384 nozomi | gzip > nozomi_$date_str.sql.gz
