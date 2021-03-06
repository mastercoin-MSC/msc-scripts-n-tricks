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
compressed = listOptions['compressed']
#print transaction

if decoderaw == 1:
    #get all multisigs
    multisig_output = []
    for output in transaction['vout']:
        if output['scriptPubKey']['type'] == 'multisig':
            multisig_output.append(output) #grab msigs
    #reference = output['scriptPubKey']['addresses'][0]
else:
    #get all multisigs
    multisig_output = []
    for output in transaction.vout:
        if output['scriptPubKey']['type'] == 'multisig':
            multisig_output.append(output) #grab msigs

#extract compressed keys
scriptkeys = []
for output in multisig_output:   #seqnums start at 1, so adjust range 
    split_script = output['scriptPubKey']['asm'].split(' ')
    for val in split_script:
        if len(val) == 66:
            scriptkeys.append(val)

#filter keys that are ref
nonrefkeys = []
for compressedkey in scriptkeys:
    if pybitcointools.pubtoaddr(compressedkey) != reference and pybitcointools.pubtoaddr(compressedkey) != compressed:
        nonrefkeys.append(compressedkey)

max_seqnum = len(nonrefkeys)
sha_keys = [ hashlib.sha256(reference).digest().encode('hex').upper()]  #first sha256 of ref addr, see class B for more info  
for i in range(max_seqnum):
    if i < (max_seqnum-1):
        sha_keys.append(hashlib.sha256(sha_keys[i]).digest().encode('hex').upper()) #keep sha'ing to generate more packets

pairs = []
for i in range(len(nonrefkeys)):
    pairs.append((nonrefkeys[i], sha_keys[i] ))

#DEBUG 
#print pairs

packets = []
for pair in pairs:
    obpacket = pair[0].upper()[2:-2]
    shaaddress = pair[1][:-2]
    print 'Obfus/SHA', obpacket, shaaddress
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



long_packet = ''
for packet in packets:
    print 'Decoded packet #' + str(packet[0:2]) + ' : ' + packet
    long_packet += packet[2:]

#DEBUG print long_packet

if long_packet[4:8] == '0032':
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Ecosystem: ' + long_packet[8:10]
    print 'Property type: ' + long_packet[10:14]
    print 'Previous property id: ' + long_packet[14:22]

    spare_bytes = []
    for i in range(0,len(long_packet[22:]),2):
        spare_bytes.append(long_packet[22:][i] + long_packet[22:][i+1])
    #DEBUG print spare_bytes

    prop_cat = ''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex') 
    print 'Property Category: ' + prop_cat

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_subcat = ''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex') 
    print 'Property Subcategory: ' + prop_subcat

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_name = ''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex') 
    print 'Property Name: ' + prop_name

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_url = ''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')
    print 'Property URL: ' +  prop_url

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_data = ''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex') 
    print 'Property Data: ' +  prop_data

    spare_bytes = ''.join(spare_bytes[spare_bytes.index('00')+1:])
    print 'Number of Properties: ' + str(int(spare_bytes[:16],16))
    print '\n'
if long_packet[4:8] == '0033':
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Ecosystem: ' + long_packet[8:10]
    print 'Property type: ' + long_packet[10:14]
    print 'Previous property id: ' + long_packet[14:22]

    spare_bytes = []
    for i in range(0,len(long_packet[22:]),2):
        spare_bytes.append(long_packet[22:][i] + long_packet[22:][i+1])
    #DEBUG print spare_bytes

    def removeUnicodeBytes(hex_str):
        temp_str=[]
        for let in hex_str:
            if ord(let) < 128:
                temp_str.append(let)
            else:
                temp_str.append('?')
        return ''.join(temp_str)

    prop_cat = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Category: ' + prop_cat

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_subcat = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Subcategory: ' + prop_subcat

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_name = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Name: ' + prop_name

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_url = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex'))
    print 'Property URL: ' +  prop_url

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_data = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Data: ' +  prop_data

    spare_bytes = ''.join(spare_bytes[spare_bytes.index('00')+1:])
    print 'Currency Identifier desired: '+str(int(spare_bytes[:8],16)), spare_bytes[:8]
    spare_bytes = ''.join(spare_bytes[8:])
    print 'Number of Properties: '+str(int(spare_bytes[:16],16))
    spare_bytes = ''.join(spare_bytes[16:])
    print 'Deadline: '+str(int(spare_bytes[:16],16))
    spare_bytes = ''.join(spare_bytes[16:])
    print 'Earlybird bonus: '+str(int(spare_bytes[:2],16))
    spare_bytes = ''.join(spare_bytes[2:4])
    print 'Percentage for issuer: '+ str(int(spare_bytes[:2],16))
    print '\n'
if long_packet[4:8] == '0000':
    print long_packet
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Currency Identifier: ' + long_packet[8:16]
    print 'Amount to transfer: ' + long_packet[16:32]
if long_packet[4:8] == '0035':
    print long_packet
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Currency Identifier: ' + long_packet[8:16]
if long_packet[4:8] == '0015':
    print long_packet
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Currency Identifier for Sale: ' + long_packet[8:16]
    print 'Amount for sale: ' + long_packet[16:32]
    print 'Currency Identifier Desired: ' + long_packet[32:40]
    print 'Amount Desired: ' + long_packet[40:56]
    print 'Action: ' + long_packet[56:58]
if long_packet[4:8] == '0036':
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Ecosystem: ' + long_packet[8:10]
    print 'Property type: ' + long_packet[10:14]
    print 'Previous property id: ' + long_packet[14:22]

    spare_bytes = []
    for i in range(0,len(long_packet[22:]),2):
        spare_bytes.append(long_packet[22:][i] + long_packet[22:][i+1])
    #DEBUG print spare_bytes

    def removeUnicodeBytes(hex_str):
        temp_str=[]
        for let in hex_str:
            if ord(let) < 128:
                temp_str.append(let)
            else:
                temp_str.append('?')
        return ''.join(temp_str)

    prop_cat = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Category: ' + prop_cat

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_subcat = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Subcategory: ' + prop_subcat

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_name = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Name: ' + prop_name

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_url = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex'))
    print 'Property URL: ' +  prop_url

    spare_bytes = spare_bytes[spare_bytes.index('00')+1:]
    prop_data = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Data: ' +  prop_data
    print '\n'
if long_packet[4:8] == '0037' or long_packet[4:8] == '0038':
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Property id: ' + long_packet[8:16]
    print 'Number of properties: ' + long_packet[16:32]
    spare_bytes = []
    for i in range(0,len(long_packet[32:]),2):
        spare_bytes.append(long_packet[32:][i] + long_packet[32:][i+1])
    #DEBUG print spare_bytes

    def removeUnicodeBytes(hex_str):
        temp_str=[]
        for let in hex_str:
            if ord(let) < 128:
                temp_str.append(let)
            else:
                temp_str.append('?')
        return ''.join(temp_str)

    prop_data = removeUnicodeBytes(''.join(spare_bytes[0:spare_bytes.index('00')]).decode('hex')) 
    print 'Property Data: ' +  prop_data
    print '\n'
