# How to use this software:
#   This program takes JSON as input and outputs debug information
#   as well as a armory-unsigned transaction in the Master Protocol
#   'cat input.json | python2 generatesend.py' begins the process
# Install
#   There are a few dependencies that can be installed using python-pip
#   Those are: bitcoin-python and pybitcointools (ex. pip install pybitcointools)
#   Also, you will need a fully synced Armory installation to generate transactions, as well as an installation of bitcoind/bitcoinqt that is fully synced.  
# License
#   Free software, do not include in commercial systems, GPL
# Contact
#   github.com/faizkhan00


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



if "--force" in sys.argv:
    #WARNING: '--force' WILL STEAL YOUR BITCOINS IF YOU DON KNOW WHAT YOU'RE DOING
    force=True
else:
    force=False

JSON = sys.stdin.readlines()

listOptions = json.loads(str(''.join(JSON)))

#sort out whether using local or remote API
conn = bitcoinrpc.connect_to_local()

#header=armoryhex[:2]
#mainhex=armoryhex[2:-2]
#footer=armoryhex[-2:]


#unsigned=conn.decoderawtransaction(mainhex2)
#unsigned={'vin': [{'txid':''},{'txid':''}]}

pubkey = listOptions['pubkey']

broadcast_fee = 0.0001  
output_minimum = 0.00006 #dust threshold

fee_total = Decimal(0.0001) + Decimal(0.00006 * 4)

vins=[]
vin_mod=0
#for vin in unsigned['vin']:
vin_range=2 if listOptions['feeSeed'] else 1
for vin in range(0,vin_range):
    inputtxid=listOptions['inputTx']
    #inputtxindex=vin['vout']+3  not fee seed
    inputtxindex=listOptions['startIndexInput']+vin_mod
    if vin_mod==0 and vin_range:
        vin_mod+=1
    inputtxdata=conn.getrawtransaction(inputtxid)
    vins.append((inputtxid,inputtxindex,inputtxdata))
    #print "INPUT TX/ID", inputtxid, inputtxindex
    #print "INPUT VOUT",inputtxdata.vout[inputtxindex],'\n'

largest_spendable_input={'value': listOptions['amountOfInput']}

#for each in vins:
#    vout_address=each[2].vout[each[1]]['scriptPubKey']['addresses']
    #vout_address = inputtxdata.vout[inputtxindex]['scriptPubKey']['addresses']
#    if (len(vout_address) > 1) and vout_address[0] != listOptions['transaction_from']:
#        print 'more than 1 address, no multisig, or transaction_from isn\'t the address in the vout', vout_address 
#        exit(1)
#    largest_spendable_input['value']+=each[2].vout[each[1]]['value']

#largest_spendable_input=inputtxdata.vout[inputtxindex]

change = Decimal(Decimal(largest_spendable_input['value']) - fee_total)

# calculate change : 
# (total input amount) - (broadcast fee) - (total transaction fee)
print "FEE TOTAL----> ",fee_total, largest_spendable_input['value']
if (Decimal(change) < Decimal(0) or fee_total > largest_spendable_input['value']) and not force:
    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#build multisig data address

from_address = listOptions['transaction_from']
transaction_type = 0   #simple send
sequence_number = 1    #packet number
currency_id = int(listOptions['currency'])        #MSC
import decimal
amount = int(decimal.Decimal(listOptions['msc_send_amt'])*decimal.Decimal(1e8))  #FIXED THE ROUNDING BUG

cleartext_packet = ( 
        (hex(sequence_number)[2:].rjust(2,"0") + 
            hex(transaction_type)[2:].rjust(8,"0") +
            hex(currency_id)[2:].rjust(8,"0") +
            hex(amount)[2:].rjust(16,"0") ).ljust(62,"0") )

sha_the_sender = hashlib.sha256(from_address).hexdigest().upper()[0:-2]
# [0:-2] because we remove last ECDSA byte from SHA digest

cleartext_bytes = map(ord,cleartext_packet.decode('hex'))  #convert to bytes for xor
shathesender_bytes = map(ord,sha_the_sender.decode('hex')) #convert to bytes for xor

msc_data_key = ''.join(map(lambda xor_target: hex(operator.xor(xor_target[0],xor_target[1]))[2:].rjust(2,"0"),zip(cleartext_bytes,shathesender_bytes))).upper()
#map operation that xor's the bytes from cleartext and shathesender together
#to obfuscate the cleartext packet, for more see Appendix Class B:
#https://github.com/faizkhan00/spec#class-b-transactions-also-known-as-the-multisig-method

obfuscated = "02" + msc_data_key + "00" 
#add key identifier and ecdsa byte to new mastercoin data key

invalid = True
while invalid:
    obfuscated_randbyte = obfuscated[:-2] + hex(random.randint(0,255))[2:].rjust(2,"0").upper()
    #set the last byte to something random in case we generated an invalid pubkey
    potential_data_address = pybitcointools.pubkey_to_address(obfuscated_randbyte)
    if bool(conn.validateaddress(potential_data_address).isvalid):
        data_pubkey = obfuscated_randbyte
        invalid = False
#make sure the public key is valid using pybitcointools, if not, regenerate 
#the last byte of the key and try again

#### Build transaction

#retrieve raw transaction to spend it

validnextinputs = []                      #get valid redeemable inputs

for each in vins:
    validnextinputs.append({ "txid": each[0], "vout": each[1]})

validnextoutputs = { "1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P": 0.00006 , listOptions['transaction_to'] : 0.00006 }

if change > Decimal(0.00006): # send anything above dust to yourself
    validnextoutputs[ listOptions['transaction_from'] ] = float(change) 

unsigned_raw_tx = conn.createrawtransaction(validnextinputs, validnextoutputs)

json_tx =  conn.decoderawtransaction(unsigned_raw_tx)

#add multisig output to json object
json_tx['vout'].append({ "scriptPubKey": { "hex": "5141" + pubkey + "21" + data_pubkey.lower() + "52ae", "asm": "1 " + pubkey + " " + data_pubkey.lower() + " 2 OP_CHECKMULTISIG", "reqSigs": 1, "type": "multisig", "addresses": [ pybitcointools.pubkey_to_address(pubkey), pybitcointools.pubkey_to_address(data_pubkey) ] }, "value": 0.00006*2, "n": len(validnextoutputs)})

#construct byte arrays for transaction 
#assert to verify byte lengths are OK
version = ['01', '00', '00', '00' ]
assert len(version) == 4

num_inputs = [str(len(json_tx['vin'])).rjust(2,"0")]
assert len(num_inputs) == 1

num_outputs = [str(len(json_tx['vout'])).rjust(2,"0")]
assert len(num_outputs) == 1

sequence = ['FF', 'FF', 'FF', 'FF']
assert len(sequence) == 4

blocklocktime = ['00', '00', '00', '00']
assert len(blocklocktime) == 4

#prepare inputs data for byte packing
inputsdata = []
for _input in json_tx['vin']:
    prior_input_txhash = _input['txid'].upper()  
    prior_input_index = str(hex(_input['vout'])[2:] ).rjust(2,"0").ljust(8,"0")  #FIXED HEX HERE
    input_raw_signature = _input['scriptSig']['hex']
    
    prior_txhash_bytes =  [prior_input_txhash[ start: start + 2 ] for start in range(0, len(prior_input_txhash), 2)][::-1]
    assert len(prior_txhash_bytes) == 32

    prior_txindex_bytes = [prior_input_index[ start: start + 2 ] for start in range(0, len(prior_input_index), 2)]
    assert len(prior_txindex_bytes) == 4

    len_scriptsig = ['%02x' % len(''.join([]).decode('hex').lower())] 
    assert len(len_scriptsig) == 1
    
    inputsdata.append([prior_txhash_bytes, prior_txindex_bytes, len_scriptsig])

#prepare outputs for byte packing
output_hex = []
for output in json_tx['vout']:
    value_hex = hex(int(float(output['value'])*1e8))[2:]
    value_hex = value_hex.rjust(16,"0")
    value_bytes =  [value_hex[ start: start + 2 ].upper() for start in range(0, len(value_hex), 2)][::-1]
    assert len(value_bytes) == 8

    scriptpubkey_hex = output['scriptPubKey']['hex']
    scriptpubkey_bytes = [scriptpubkey_hex[start:start + 2].upper() for start in range(0, len(scriptpubkey_hex), 2)]
    len_scriptpubkey = ['%02x' % len(''.join(scriptpubkey_bytes).decode('hex').lower())]
    #assert len(scriptpubkey_bytes) == 25 or len(scriptpubkey_bytes) == 71

    output_hex.append([value_bytes, len_scriptpubkey, scriptpubkey_bytes] )

#join parts into final byte array
hex_transaction = version + num_inputs

for _input in inputsdata:
    hex_transaction += (_input[0] + _input[1] + _input[2] + sequence)

hex_transaction += num_outputs

for output in output_hex:
    hex_transaction = hex_transaction + (output[0] + output[1] + output[2]) 

hex_transaction = hex_transaction + blocklocktime
hex_transaction2=''.join(hex_transaction).lower()
#verify that transaction is valid
decoded_hex=conn.decoderawtransaction(''.join(hex_transaction).lower())
assert type(decoded_hex) == type({})

print "\nRAW HEX -------------------------------------------->\n\n"
print '\n',hex_transaction2

import pprint
print "\nTRANSACTION WILL LOOK LIKE----------------------------------->\n\n"
print pprint.pprint(decoded_hex)
#print json.dumps(decoded_hex, sort_keys=True,indent=4, separators=(',', ': '))
listOptions['decoderaw']=hex_transaction2

#get transaction to decode multisig addr
decoderaw = 1
transaction = conn.decoderawtransaction(listOptions['decoderaw'])

#reference/senders address
reference = listOptions['transaction_from']

if decoderaw == 1:
    #get all multisigs
    multisig_output = []
    for output in transaction['vout']:
        if output['scriptPubKey']['type'] == 'multisig':
            multisig_output.append(output) #grab msigs
    #reference = output['scriptPubKey']['addresses'][0]

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
    if pybitcointools.pubtoaddr(compressedkey) != reference:
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

if long_packet[4:8] == '0000':
    print long_packet
    print 'Tx version: ' + long_packet[0:4]
    print 'Tx type: ' + long_packet[4:8]
    print 'Currency Identifier: ' + long_packet[8:16]
    print 'Amount to transfer: ' + long_packet[16:32] + '\n\nYOU ARE SENDING -----------------------------------------> ' + str(int(long_packet[16:32],16))

import sys
sys.path.append("/usr/lib/armory/")
from armoryengine.ALL import *

walletPath = listOptions['wallet']
hexRawTxn = hex_transaction2

try:
	wlt = PyBtcWallet().readWalletFile(walletPath)
	# Register wallet and start blockchain scan
	TheBDM.registerWallet(wlt)
	TheBDM.setBlocking(True)
	TheBDM.setOnlineMode(True)  # will take 20 min for rescan
	# Need "syncWithBlockchain" every time TheBDM is updated
	wlt.syncWithBlockchain()
except Exception,e:
	print 'STATE: ', TheBDM.getBDMState()
	print 'ERROR: ', e

try:
	while not TheBDM.getBDMState()=='BlockchainReady':
		import time
		time.sleep(2)
		print 'Armory blockchain not ready: ', TheBDM.getBDMState()
	#Translate raw txn
	pytx = PyTx()
	print("Encoding raw txn: %s" % hexRawTxn)
	binTxn = hex_to_binary(hexRawTxn)
	pytx.unserialize(binTxn)
	tx = PyTxDistProposal(pytx)
	print("\n\nOutput is:\n%s" % tx.serializeAscii())

	TheBDM.execCleanShutdown()
except Exception,e:
	print 'STATE: ', TheBDM.getBDMState(), ' ', TheBDM.getBlkMode()
	print 'ERROR: ', e
