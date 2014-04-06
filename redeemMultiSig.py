#get balance
import sys
import json
import time
import random
import hashlib
import operator
import bitcoinrpc
import pybitcointools
from decimal import *


if len(sys.argv) > 1 and "--force" not in sys.argv: 
    print "Takes a list of bitcoind options, addresses and a send amount and outputs a transaction in JSON \nUsage: cat generateTx.json | python generateTx.py\nRequires a fully-synced *local* bitcoind node"
    exit()

if "--force" in sys.argv:
    #WARNING: '--force' WILL STEAL YOUR BITCOINS IF YOU DON KNOW WHAT YOU'RE DOING
    force=True
else:
    force=False

JSON = sys.stdin.readlines()

listOptions = json.loads(str(''.join(JSON)))

#sort out whether using local or remote API
conn = bitcoinrpc.connect_to_local()

#check if private key provided produces correct address
address = pybitcointools.privkey_to_address(listOptions['from_private_key'])
if not address == listOptions['transaction_from'] and not force:
    print json.dumps({ "status": "NOT OK", "error": "Private key does not produce same address as \'transaction from\'" , "fix": "Set \'force\' flag to proceed without address checks" })
    exit()

#see if account has been added
account = conn.getaccount(listOptions['transaction_from'])
if account == "" and not force:
    _time = str(int(time.time()))
    private = listOptions['from_private_key']
    print json.dumps({ "status": "NOT OK", "error": "Couldn\'t find address in wallet, please run \'fix\' on the machine", "fix": "bitcoind importprivkey " + private + " imported_" + _time  })

#calculate minimum unspent balance
available_balance = Decimal(0.0)

validated = conn.validateaddress(listOptions['transaction_from'])
if 'pubkey' in validated.__dict__: 
    pubkey = validated.pubkey

unspent_tx = []
error_tx = []
processed_txes = []
import commands
for transaction in conn.listtransactions(account,999999):
    if transaction.txid not in processed_txes:
        processed_txes.append(transaction.txid)
        try:
            tx = conn.getrawtransaction(transaction.txid)
            for output in tx.vout:
                if output['scriptPubKey']['type']=='multisig' and pubkey in output['scriptPubKey']['asm'].split(' '):
                    if commands.getoutput('bitcoind gettxout ' +  str(transaction.txid) + ' ' + str(output['n'])) != '':
                        #print output['value']
                        #exit()
                        #unspent_tx.append([transaction.txid, output['n']])

                        unspent_tx.append([ { "txid": transaction.txid, "vout": output['n']}, output['value'] ])
        except Exception,e:
            error_tx.append(transaction.txid)
            #Transaction probably not found, don't worry
            pass

validnextinputs = []
total_val = float(0.0)
for input_ in unspent_tx:
    validnextinputs.append(input_[0])
    total_val += float(input_[1])

#print total_val
unsigned_raw_tx = conn.createrawtransaction(validnextinputs, { listOptions['transaction_to'] : float(total_val)-0.0002 } )
signed_transaction = conn.signrawtransaction(unsigned_raw_tx)

#output final product as JSON
print json.dumps({ "rawtransactions": signed_transaction})

