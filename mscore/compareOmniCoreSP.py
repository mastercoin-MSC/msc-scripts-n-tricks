import json
a=json.loads(''.join(open('consensus/parsed-addrs.txt').readlines()))
b=json.loads(open('consensus/omni.txt').readline())

notmatching=[]

for addr in a:
    addr__=addr['address']
    bal=('%.8f' % float(addr['balance']) ) 
    res = ('%.8f' % float(addr['reservedbyoffer']) )

    for addr_ in b:
        #print bal, addr__, res, addr_
        bal_ = ( '%.8f' % float(addr_['balance']))
        res_ = ( '%.8f' % float(addr_['reserved_balance']))
        if addr__ == addr_['address']:
            notmatching.append(addr__)
            if (bal != bal_ or res != res_):
                print '\n',addr__, bal, res, addr_
                #exit()


for addr in a:
    if addr['address'] not in notmatching:
        print "couldn't find ", addr['address'], ' in testaddrs'
    
for addr in b:
    if addr['address'] not in notmatching:
        print "couldn't find ", addr['address'], ' in canonical'
