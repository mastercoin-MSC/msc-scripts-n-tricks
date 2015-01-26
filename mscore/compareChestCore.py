import json
a=open('consensus/parsed-addrs.txt').readlines()
b=json.loads(open('consensus/chest.txt').readline())

notmatching=[]

for addr in a:
    splitaddr=addr.split('+')
    addr__=splitaddr[0]
    bal= splitaddr[1] 
    sores= splitaddr[2][:-1] if splitaddr[2][-1] == '\n' else splitaddr[2] 
    #acres= splitaddr[3][:-1] if splitaddr[3][-1] == '\n' else splitaddr[3] 
    res = ('%.8f' % (float(sores) + float(0)) )


    for addr_ in b:
        #print bal, addr__, res, addr_
        if addr__ == addr_['address'] and ( bal != ( '%.8f' % float(addr_['balance']))):
                #or res != ( '%.8f' % float(addr_['reserved_balance'])) ):
            print '\n',addr__, bal, res, addr_
            #exit()
