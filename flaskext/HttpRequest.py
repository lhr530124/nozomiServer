import urllib, urllib2

def requestGet(url, params):
    rurl = url + "?" + urllib.urlencode(params)
    print(rurl)
    req = urllib2.Request(rurl)
    page = urllib2.urlopen(req)
    return page.readlines()

def requestPost(url, params):
    data = urllib.urlencode(params)
    req = urllib2.Request(url)
    page = urllib2.urlopen(req, data)
    return page.readlines()
