import json
f = open('../stat.log')
title = ['ZOMBIE', 'ZOMBIE_DEFEND', 'ZOMBIE_SKIP', 'ATTACK', 'BATTLE_END', 'BATTLE_END_VIDEO', 'HISTORY', 'VIDEO_DOWNLOAD', 'DOWNLOAD', 'SHARE', 'NIGHT']
count = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
for l in f.readlines():
    row = l.split() 
    #print row
    try:
        row = json.loads(row[3])
    except:
        #finidlog error
        continue
        pass
    for i in xrange(0, len(row)):
        count[i] += row[i]
for i in xrange(0, len(title)):
    print title[i], 
    print count[i]
