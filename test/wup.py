up = 'update='
res = []
for i in xrange(1, 500):
    res.append({'buildIndex':i, 'grid':100400, 'bid':3006, 'level':5, 'time':0, 'hitpoints':100})
import json
data = {
'uid':3,
'up': json.dumps(res)
}
import urllib
print urllib.urlencode(data)
#print len(up)
    
