import json
f = open('../crystal_stat.log')
title = ['ACC_BUILD', 'ACC_SOLDIER', 'BUY_SOLDIER', 'BUY_RESOURCE', 'BUY_SHIELD', 'BUY_ZOMBIE_SHIELD']
count = [0, 0, 0, 0, 0, 0]
cost = [0, 0, 0, 0, 0, 0]
for l in f.readlines():
    row = l.split()    
    #print row
    oldRow = row
    row = ''.join(row[3:])
    try:
        row = json.loads(row)
    except:
        print "error", oldRow
        continue
        pass
    try:
        count[row[0]-1] += 1
        cost[row[0]-1] += row[2]
    except:
        print "error2", row
    
for i in xrange(0, len(title)):
    print title[i], count[i], cost[i]
     

