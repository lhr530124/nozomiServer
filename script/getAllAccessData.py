#coding:utf8
f = open('../nozomiAccess.log')
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
        v = costTime.setdefault(reqUrl, 0)
        v += int(w[2])
        costTime[reqUrl] = v
print costTime
