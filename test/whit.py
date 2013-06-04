import json
import urllib
res = []
for i in xrange(1, 300):
    res.append([i, 10])
data = {
'uid':3,
'hits': json.dumps(res)
}

print urllib.urlencode(data)

