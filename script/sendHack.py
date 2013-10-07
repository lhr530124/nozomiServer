import urllib
import urllib2
data = {
'uid':1,
'name':'Caesars Studio',
'cid':0,
'text':'Hackers are forbidden! We will kick all hackers out when found.'
}
r = urllib.urlopen('http://localhost:8005/send?'+urllib.urlencode(data))
l = r.read()
print l

