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
    print "\ncat deobfus.json| python2 deobfus.py, see https://github.com/curtislacy/msc-exchange-scripts/pull/6 for more"
    exit()

JSON = sys.stdin.readlines()

listOptions = json.loads(str(''.join(JSON)))

#sort out whether using local or remote API
conn = bitcoinrpc.connect_to_local()

#get transaction to decode multisig addr
decoderaw = 0
if listOptions['decoderaw'] != "":
    decoderaw = 1
    transaction = conn.decoderawtransaction(listOptions['decoderaw'])
else:
    transaction = conn.getrawtransaction(listOptions['transaction'])

#reference/senders address
reference = listOptions['reference']

if decoderaw == 1:
    #get all multisigs
    multisig_output = []
    for output in transaction['vout']:
        if output['scriptPubKey']['type'] == 'multisig':
            multisig_output.append(output) #grab msigs
else:
    #get all multisigs
    multisig_output = []
    for output in transaction.vout:
        if output['scriptPubKey']['type'] == 'multisig':
            multisig_output.append(output) #grab msigs
    
#extract compressed keys
scriptkeys = []
for output in multisig_output:
    split_script = output['scriptPubKey']['asm'].split(' ')
    for val in split_script:
        if len(val) == 66:
            scriptkeys.append(val)

#filter keys that are ref
nonrefkeys = []
for compressedkey in scriptkeys:
    if pybitcointools.pubtoaddr(compressedkey) != reference:
        nonrefkeys.append(compressedkey)

sha_keys = []
for i in range(len(nonrefkeys)):
    if i < len(nonrefkeys):
        sha_keys.append(hashlib.sha256(reference).digest().encode('hex').upper()) #first sha256 of ref addr, see class B for more info 
    if i < (len(nonrefkeys)-1):
        sha_keys.append(hashlib.sha256(sha_keys[i]).digest().encode('hex').upper()) #keep sha'ing to generate more packets

pairs = zip(nonrefkeys,sha_keys)

#DEBUG 
print pairs
packets = []
for pair in pairs:
    obpacket = pair[0].upper()[2:-2]
    shaaddress = pair[1][:-2]
    datapacket = ''
    for i in range(len(obpacket)):
        if obpacket[i] == shaaddress[i]:
            datapacket = datapacket + '0'
        else:
            bin_ob = int('0x' + obpacket[i], 16)
            bin_sha = int('0x' + shaaddress[i], 16)
            xored = hex(bin_ob ^ bin_sha)[2:].upper()
            datapacket = datapacket + xored
    packets.append(datapacket)


count = 0
for packet in packets:
    count = count + 1
    print 'Decoded packet #' + str(count) + ' : ' + packet
    if count == 1:
        print 'Seq #?: ' + packet[:2]
        print 'Tx version: ' + packet[2:6]
        print 'Tx type: ' + packet[6:10]
        print 'Currency: ' + packet[10:18]
        print '\n'
    else:
        print 'Seq #?: ' + packet[:2]
        print '\n'
