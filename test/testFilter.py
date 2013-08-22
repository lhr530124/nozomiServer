from testConfig import *
r = base2+'checkKeyWord?'+urllib.urlencode({'word':"fuck fuck you"})
req(r)

r = base2+'blockWord?'+urllib.urlencode({'word':'fuck fuck you'})
req(r)
