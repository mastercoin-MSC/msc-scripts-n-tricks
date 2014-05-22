#get balance
import sys
import json

if len(sys.argv) > 1: 
    print "Takes a list of MSC addresses and outputs a balance in JSON \nUsage: cat listOfAddresses.json | python2 getBalanceMSC.py\nRequires a fully-synced omniwallet node"
    exit()

tmp='/tmp/omniwallet/addr/'    

JSON = sys.stdin.readlines()

listAddresses = json.loads(str(''.join(JSON)))
results = []
for addr in listAddresses['addresses']:
    try:
        f=open(tmp + addr + '.json')
        address = json.loads(f.readline())
        results.append({ 'address': address['address'], 'balance': address['balance']})
    except IOError:
        results.append({'address': "No such MSC address " + addr, 'balance': 'NOT OK'})

print json.dumps(results)
