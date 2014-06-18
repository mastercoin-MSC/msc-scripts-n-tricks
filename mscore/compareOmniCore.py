import json
a=open('parsed-addrs.txt').readlines()
b=json.loads(open('omni.txt').readline())

notmatching=[]

for addr in a:
    splitaddr=addr.split('+')
    addr__=splitaddr[0]
    bal= splitaddr[1] 
    res= splitaddr[2][:-1] if splitaddr[2][-1] == '\n' else splitaddr[2] 

    
    for addr_ in b:
        #print bal, addr__, res, addr_
        if addr__ == addr_['address'] and ( bal != ( '%.8f' % float(addr_['balance'])) or res != ( '%.8f' % float(addr_['reserved_balance'])) ):
            print '\n',addr__, bal, res, addr_
            #exit()
