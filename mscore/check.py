import sys
import json
import commands
import requests
import time
#a=json.loads(''.join(open('adamscons.txt').readlines()))
#b=json.loads(''.join(open('adamscons-omni.txt').readlines()))

#a=json.loads(''.join(open('maidsafecoin.txt').readlines()))
#b=json.loads(''.join(open('maidsafecoin-omni.txt').readlines()))

verbose=False
if len(sys.argv) > 1 and int(sys.argv[1]) == 1:
    verbose=True

props=json.loads(''.join(open('props.txt').readlines()))

props.insert(0,{'currencyID': 2, 'name': 'Test Mastercoin'})
props.insert(0,{'currencyID': 1, 'name': 'Mastercoin'})
bads = []
missing = []
data = []
for id_ in props:
    id_ = str(id_['currencyID'])
#for id_ in ['2147483659','2147483694','2147483700', '2147483698','2147483661','2147483653','2147483697']:
    print 'checking...', id_
    output=json.loads(''.join(commands.getoutput('./../bitcoind getallbalancesforid_MP '+id_)))#+id_['currencyID'])
    print 'making request...'

    upstream=requests.get('http://localhost/v1/mastercoin_verify/addresses?currency_id='+id_).json()
    #upstream=requests.get('https://www.omniwallet.org/v1/mastercoin_verify/addresses?currency_id='+id_).json()
    try:
        pass
        #time.sleep(1)
        #upstream=requests.get('https://masterchest.info/mastercoin_verify/addresses.ASPX?currencyid='+id_).json()
    except Exception, e:
        print e, 'retrying...'
        #upstream=requests.get('https://masterchest.info/mastercoin_verify/addresses.ASPX?currencyid='+id_).json()
    data.append([id_,output,upstream])
    print 'done.'

for id_ in data:
    upstream = id_[2]
    output = id_[1]
    id_ = id_[0]

    upstream_addrs=[]
    for each in upstream:
        upstream_addrs.append(each['address']) 

    print 'id is: ', id_
    for each in output:
        if each['address'] not in upstream_addrs:
            if verbose:
                print 'FUK!!!', each['address']
            missing.append([id_,each])
        for eacher in upstream: 
            if each['address'] == eacher['address']:
                if verbose:
                    print 'compare: ', each['address'], eacher['address']
                    print 'balance: ', each['balance'], eacher['balance']
                if float(each['balance']) != float(eacher['balance']):
                    bads.append([id_,each,eacher])
                    if verbose:
                        print 'FUK!!!', each['balance'], eacher['balance']



print 'Differences between mastercore and your upstream source:'
for each in bads:
    print each

print 'Missing addresses between mastercore and your upstream source:'
for each in missing:
    if float(each[1]['balance']) > 0:
        print each
    else: 
        if verbose:
            print each
