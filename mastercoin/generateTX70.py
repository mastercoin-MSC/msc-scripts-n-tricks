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

HEXSPACE_SECOND='21'

mainnet_exodus_address='1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P'
testnet_exodus_address='mpexoDuSkGGqvqrkrjiFng38QPkJQVFyqv'
moneyman='moneyqMan7uh8FqdCA2BV5yZ8qVrc9ikLP'
magicbyte=0
testnet=False
exodus_address=mainnet_exodus_address

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

if listOptions['testnet']:
    testnet =True
    magicbyte =111
    exodus_address=testnet_exodus_address

#check if private key provided produces correct address
address = pybitcointools.privkey_to_address(listOptions['from_private_key'], magicbyte)
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

unspent_tx = []
for unspent in conn.listunspent():
    if unspent.address == listOptions['transaction_from']:
        unspent_tx.append(unspent)
#get all unspent for our from_address

for unspent in unspent_tx:
   available_balance = unspent.amount + available_balance

#check if minimum BTC balance is met
if available_balance < Decimal(0.0006*3) and not force:
    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#generate public key of bitcoin address 
validated = conn.validateaddress(listOptions['transaction_from'])
if 'pubkey' in validated.__dict__: 
    pubkey = validated.pubkey
    if len(pubkey) < 100:
        print "Compressed Key, using hexspace 21"
        HEXSPACE_FIRST='21'
    else:
        HEXSPACE_FIRST='41'
elif not force:
    print json.dumps({ "status": "NOT OK", "error": "from address is invalid or hasn't been used on the network" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#find largest spendable input from UTXO
largest_spendable_input = { "txid": "", "amount": Decimal(0) }
for unspent in unspent_tx:
    if unspent.amount > largest_spendable_input["amount"]:
        largest_spendable_input = { "txid": unspent.txid, "amount": unspent.amount }

#real stuff happens here:

#build multisig data address
transaction_version = 0
transaction_type = listOptions['transaction_type']
property_id = listOptions['property_id']

#calculate bytes
tx_ver_bytes = hex(transaction_version)[2:].rjust(4,"0") # 2 bytes
tx_type_bytes = hex(transaction_type)[2:].rjust(4,"0")   # 2 bytes
prop_id_bytes = hex(property_id)[2:].rjust(8,"0")  # 4 bytes

total_bytes = (len(tx_ver_bytes) + 
               len(tx_type_bytes) + 
               len(prop_id_bytes))/2

byte_stream = tx_ver_bytes + tx_type_bytes + prop_id_bytes

import math
total_packets = int(math.ceil(float(total_bytes)/30)) #get # of packets

total_outs = int(math.ceil(float(total_packets)/2)) #get # of outs

#construct packets
packets = []
index = 0
for i in range(total_packets):
    # 2 multisig data addrs per out, 60 bytes per, 2 characters per byte so 60 characters per pass
    parsed_data = byte_stream[index:index+60].ljust(60,"0")
    cleartext_packet =  (hex(i+1)[2:].rjust(2,"0") + parsed_data.ljust(60,"0"))

    index = index+60
    packets.append(cleartext_packet)
    #DEBUG print ['pax',cleartext_packet, parsed_data, total_packets, i]


from_address = listOptions['transaction_from']
obfuscation_packets = [hashlib.sha256(from_address).hexdigest().upper()]  #add first sha of sender to packet list
for i in range(total_packets-1): #do rest for seqnums
    obfuscation_packets.append(hashlib.sha256(obfuscation_packets[i]).hexdigest().upper())

#DEBUG print [packets,obfuscation_packets, len(obfuscation_packets[0]), len(obfuscation_packets[1]), len(packets[0])]

#obfuscate and prepare multisig outs
pair_packets = []
for i in range(total_packets):
    obfuscation_packet = obfuscation_packets[i]
    pair_packets.append((packets[i], obfuscation_packet[:-2]))

#encode the plaintext packets
obfuscated_packets = []
for pair in pair_packets:
    plaintext = pair[0].upper()
    shaaddress = pair[1] 
    #DEBUG print ['packets', plaintext, shaaddress, len(plaintext), len(shaaddress)]
    datapacket = ''
    for i in range(len(plaintext)):
        if plaintext[i] == '0':
            datapacket = datapacket + shaaddress[i]
        else:
            bin_plain = int('0x' + plaintext[i], 16)
            bin_sha = int('0x' + shaaddress[i], 16)
            #DEBUG print ['texts, plain & addr', plaintext[i], shaaddress[i],'bins, plain & addr', bin_plain, bin_sha ]
            xored = hex(bin_plain ^ bin_sha)[2:].upper()
            datapacket = datapacket + xored
    obfuscated_packets.append(( datapacket, shaaddress))

#### Test that the obfuscated packets produce the same output as the plaintext packet inputs ####

#decode the obfuscated packet
plaintext_packets = []
for pair in obfuscated_packets:
    obpacket = pair[0].upper()
    shaaddress = pair[1]
    #DEBUG print [obpacket, len(obpacket), shaaddress, len(shaaddress)]
    datapacket = ''
    for i in range(len(obpacket)):
        if obpacket[i] == shaaddress[i]:
            datapacket = datapacket + '0'
        else:
            bin_ob = int('0x' + obpacket[i], 16)
            bin_sha = int('0x' + shaaddress[i], 16)
            xored = hex(bin_ob ^ bin_sha)[2:].upper()
            datapacket = datapacket + xored
    plaintext_packets.append(datapacket)

#check the packet is formed correctly by comparing it to the input
final_packets = []
for i in range(len(plaintext_packets)):
    orig = packets[i]
    if orig.upper() != plaintext_packets[i]:
        print ['packet did not come out right', orig, plaintext_packets[i] ]
    else:
        final_packets.append(obfuscated_packets[i][0])

#DEBUG print plaintext_packets, obfuscation_packets,final_packets

#add key identifier and ecdsa byte to new mastercoin data key
for i in range(len(final_packets)):
    obfuscated = '02' + final_packets[i] + "00" 
    #DEBUG print [obfuscated, len(obfuscated)]
    invalid = True
    while invalid:
        obfuscated_randbyte = obfuscated[:-2] + hex(random.randint(0,255))[2:].rjust(2,"0").upper()
        #set the last byte to something random in case we generated an invalid pubkey
        potential_data_address = pybitcointools.pubkey_to_address(obfuscated_randbyte, magicbyte)
        if bool(conn.validateaddress(potential_data_address).isvalid):
            final_packets[i] = obfuscated_randbyte
            invalid = False
    #make sure the public key is valid using pybitcointools, if not, regenerate 
    #the last byte of the key and try again

#DEBUG print final_packets

#### Build transaction

#calculate fees
fee_total = Decimal(0.0001) + Decimal(0.000055*total_packets+0.000055*total_outs) + Decimal(0.000055)
change = largest_spendable_input['amount'] - fee_total
# calculate change : 
# (total input amount) - (broadcast fee)

if Decimal(change) < Decimal(0) or fee_total > largest_spendable_input['amount'] and not force:
    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#retrieve raw transaction to spend it
prev_tx = conn.getrawtransaction(largest_spendable_input['txid'])

validnextinputs = []                      #get valid redeemable inputs
for output in prev_tx.vout:
    if output['scriptPubKey']['reqSigs'] == 1 and output['scriptPubKey']['type'] != 'multisig':
        for address in output['scriptPubKey']['addresses']:
            if address == listOptions['transaction_from']:
                validnextinputs.append({ "txid": prev_tx.txid, "vout": output['n']})

if len( listOptions['transaction_to'] ) >= 34:
  validnextoutputs = { exodus_address: 0.000055, listOptions['transaction_to']: 0.000055 }
else:
  validnextoutputs = { exodus_address: 0.000055 }

if change > Decimal(0.000055): # send anything above dust to yourself
    validnextoutputs[ listOptions['transaction_from'] ] = float(change) 

unsigned_raw_tx = conn.createrawtransaction(validnextinputs, validnextoutputs)

json_tx =  conn.decoderawtransaction(unsigned_raw_tx)

#append  data structure
ordered_packets = []
for i in range(total_outs):
    ordered_packets.append([])

#append actual packet
index = 0
for i in range(total_outs):
    while len(ordered_packets[i]) < 2 and index != len(final_packets):
        ordered_packets[i].append(final_packets[index])
        index = index + 1
#DEBUG print ordered_packets

for i in range(total_outs):
    hex_string = "51" + HEXSPACE_FIRST + pubkey
    asm_string = "1 " + pubkey
    addresses = [ pybitcointools.pubkey_to_address(pubkey, magicbyte)]
    n_count = len(validnextoutputs)+i
    total_sig_count = 1
    #DEBUG print [i,'added string', ordered_packets[i]]
    for packet in ordered_packets[i]:
        hex_string = hex_string + HEXSPACE_SECOND + packet.lower() 
        asm_string = asm_string + " " + packet.lower()
        addresses.append(pybitcointools.pubkey_to_address(packet, magicbyte))
        total_sig_count = total_sig_count + 1
    hex_string = hex_string + "5" + str(total_sig_count) + "ae"
    asm_string = asm_string + " " + str(total_sig_count) + " " + "OP_CHECKMULTISIG"
    #DEBUG print [hex_string, asm_string, addresses,total_sig_count]
    #add multisig output to json object
    json_tx['vout'].append(
        { 
            "scriptPubKey": 
            { 
                "hex": hex_string, 
                "asm": asm_string, 
                "reqSigs": 1, 
                "type": "multisig", 
                "addresses": addresses 
            }, 
            "value": 0.000055*len(addresses), 
            "n": n_count
        })

#print json_tx

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
    prior_input_index = str(_input['vout']).rjust(2,"0").ljust(8,"0")
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
    
   # print output
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

#verify that transaction is valid
assert type(conn.decoderawtransaction(''.join(hex_transaction).lower())) == type({})

#sign it
signed_transaction = conn.signrawtransaction(''.join(hex_transaction))

#output final product as JSON
print json.dumps({ "rawtransaction": signed_transaction })

