#coding:utf8
f = open('../nozomiAccess_2.log')
lines = f.readlines()
f.close()
costTime = {}#url time
for l in lines:
    w = l.split()
    if len(w) >= 3:
        s = w[0].rfind('/')
        e = w[0].rfind('?')
        if e == -1:
            e = None
        reqUrl = w[0][s+1:e]
        v = costTime.setdefault(reqUrl, [0, 0])
        v[0] += int(w[2])
        v[1] += 1 
        costTime[reqUrl] = v

print costTime
for k in costTime:
    print k, costTime[k], costTime[k][0]/costTime[k][1]
