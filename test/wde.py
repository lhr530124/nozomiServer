de = 'delete=['
a = 500
for i in xrange(0, a):
    de += '%d,' % (i)
de += '%d]' % (a)
print de
