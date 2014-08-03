import json
a=json.loads(open('consensus/omni.txt').readline())
b=json.loads(open('consensus/chest.txt').readline())

notmatching=[]

for addr in a:
    addr__=addr['address']
    bal=addr['balance'] 
    sores= addr['reserved_balance']
    #acres= splitaddr[3][:-1] if splitaddr[3][-1] == '\n' else splitaddr[3] 
    res = ('%.8f' % (float(sores) + float(0)) )

    for addr_ in b:
        #print bal, addr__, res, addr_
        if addr__ == addr_['address']:
            notmatching.append(addr__)
            if ( str(bal) != addr_['balance']):
                #or res != ( '%.8f' % float(addr_['reserved_balance'])) ):
                print '\n',addr__, bal, res, addr_
                #exit()

for addr in a:
    addr__ = addr['address']
    if addr__ not in notmatching:
        print "couldn't find ", addr__, ' from matched addrs - a'
    
for addr in b:
    if addr['address'] not in notmatching:
        print "couldn't find ", addr['address'], ' from matched addrs - b'

print len(a), len(b), len(notmatching)
