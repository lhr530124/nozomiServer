import os
f = open('table.sql').readlines()
for l in f:
    l = l.replace('\n', '')
    if l == 'nozomi_clan_check':
        os.system('mysql -unozomi -pHff9F3TtWc17 -e "create table  test.%s like nozomi.%s; insert into test.%s select * from nozomi.%s;" ' % (l, l, l, l))
    #if l != 'nozomi_user' and l != 'nozomi_build' and l != 'nozomi_replace':
    #    os.system('mysql -unozomi -pHff9F3TtWc17 -e "truncate test.%s; insert into test.%s select * from nozomi.%s;" ' % (l, l, l))

