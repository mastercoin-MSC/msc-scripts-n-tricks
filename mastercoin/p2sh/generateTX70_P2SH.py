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

#this is not a command line tool. do not use it as such

if len(sys.argv) < 2: 
    exit()

force=False

if sys.argv[1] == '-ui':
  import CLI_prompter
  listOptions = CLI_prompter.callCLI(70)
else:
  listOptions = { 
          "transaction_type": int(sys.argv[1]), 
          "property_id": int(sys.argv[2]),

          "redeemer_addr": sys.argv[3],
          "transaction_from": sys.argv[4],
          "transaction_to": sys.argv[5],
          "spending_txid": sys.argv[6],
          "spending_txid_output": float(sys.argv[7]),
          "testnet": bool(int(sys.argv[8])) # 0 or 1
      }

HEXSPACE_SECOND='21'

if listOptions['testnet']:
    testnet=True
    magicbyte=111
else:
    testnet=False
    magicbyte=0

if sys.argv[1] == '-ui':
  if listOptions['conndetails'][0] == 'local':
    conn = bitcoinrpc.connect_to_local()
  elif listOptions['conndetails'][0] == 'remote':
    conndetails=open( listOptions['conndetails'][1] ).readline().split(':')
    conn = bitcoinrpc.connect_to_remote(conndetails[0],conndetails[1],host=conndetails[2],port=int(conndetails[3]),use_https=int(conndetails[4]))
  else:
    print 'connection did not establish: FAIL'
    exit()
else:
  if sys.argv[9] == 'local':
    conn = bitcoinrpc.connect_to_local()
  elif sys.argv[9] == 'remote':
    conndetails=open(sys.argv[10]).readline().split(':')
    #print conndetails, int(conndetails[4])
    #sort out whether using local or remote API
    conn = bitcoinrpc.connect_to_remote(conndetails[0],conndetails[1],host=conndetails[2],port=int(conndetails[3]),use_https=int(conndetails[4]))
  else:
    print 'connection did not establish: FAIL'
    exit()

#print '\n conndet', conndetails, conn.getinfo()
#check if private key provided produces correct address
#address = pybitcointools.privkey_to_address(listOptions['from_private_key'], magicbyte)
#if not address == listOptions['transaction_from'] and not force:
#    print json.dumps({ "status": "NOT OK", "error": "Private key does not produce same address as \'transaction from\'" , "fix": "Set \'force\' flag to proceed without address checks" })
#    exit()

#see if account has been added
#account = conn.getaccount(listOptions['transaction_from'])
#if account == "" and not force:
#    _time = str(int(time.time()))
#    private = listOptions['from_private_key']
#    print json.dumps({ "status": "NOT OK", "error": "Couldn\'t find address in wallet, please run \'fix\' on the machine", "fix": "bitcoind importprivkey " + private + " imported_" + _time  })

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
#if available_balance < Decimal(0.00006*3) and not force:
#    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
#    exit()

if sys.argv[1] == '-ui':
#generate public key of bitcoin address 
  if listOptions['redeemer_addr'][0] == 'pubkey':
    pubkey = listOptions['redeemer_addr'][1]
  else:
    validated = conn.validateaddress(listOptions['redeemer_addr'][1])
    if 'pubkey' not in validated.__dict__: 
        print 'NO PUBLIC KEY FOR ADDRESS FOUND IN WALLET', listOptions['redeemer_addr'][1]
    else:
        pubkey = validated.pubkey
else:
    validated = conn.validateaddress(listOptions['redeemer_addr'])
    if 'pubkey' not in validated.__dict__: 
        print 'NO PUBLIC KEY FOR ADDRESS FOUND IN WALLET', listOptions['redeemer_addr']
    else:
        pubkey = validated.pubkey

#elif not force:
#    print json.dumps({ "status": "NOT OK", "error": "from address is invalid or hasn't been used on the network" , "fix": "Set \'force\' flag to proceed without balance checks" })
#    exit()

#elif not force:
#    print json.dumps({ "status": "NOT OK", "error": "from address is invalid or hasn't been used on the network" , "fix": "Set \'force\' flag to proceed without balance checks" })
#    exit()

#find largest spendable input from UTXO
largest_spendable_input = { "txid": listOptions['spending_txid'], "amount": Decimal( listOptions['spending_txid_output']) }
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
prop_id_bytes = hex(property_id)[2:].rstrip("L").rjust(8,"0")  # 4 bytes
num_prop_bytes = hex(number_properties)[2:].rjust(16,"0")# 8 bytes











total_bytes = (len(tx_ver_bytes) + 
               len(tx_type_bytes) + 
               len(prop_id_bytes))/2


byte_stream = (tx_ver_bytes + 
               tx_type_bytes + 
               prop_id_bytes)


#DEBUG print [tx_ver_bytes,tx_type_bytes,eco_bytes,prop_type_bytes,prev_prop_id_bytes,num_prop_bytes,prop_cat_bytes,prop_subcat_bytes,prop_name_bytes,prop_url_bytes,prop_data_bytes]

#DEBUG print [len(tx_ver_bytes)/2,len(tx_type_bytes)/2,len(eco_bytes)/2,len(prop_type_bytes)/2,len(prev_prop_id_bytes)/2,len(num_prop_bytes)/2,len(prop_cat_bytes)/2,len(prop_subcat_bytes)/2,len(prop_name_bytes)/2,len(prop_url_bytes)/2,len(prop_data_bytes)/2]
                                                                                                                             
#DEBUG print [byte_stream, total_bytes]

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

if listOptions['transaction_to'] != None and bool(conn.validateaddress(listOptions['transaction_to']).isvalid):
  fee_total += Decimal(0.000055)

change = largest_spendable_input['amount'] - fee_total
# calculate change : 
# (total input amount) - (broadcast fee)
#if (Decimal(change) < Decimal(0) or fee_total > largest_spendable_input['amount']) and not force:
#    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
#    exit()

#retrieve raw transaction to spend it
prev_tx = conn.getrawtransaction(largest_spendable_input['txid'])

validnextinputs = []                      #get valid redeemable inputs
for output in prev_tx.vout:
    if output['scriptPubKey']['reqSigs'] == 1 and output['scriptPubKey']['type'] != 'multisig':
        for address in output['scriptPubKey']['addresses']:
            if address == listOptions['transaction_from']:
                p2sh_rscript = conn.validateaddress(listOptions['transaction_from']).hex
                p2sh_scriptPubkey = output['scriptPubKey']['hex']
                validnextinputs.append({ "txid": prev_tx.txid, "vout": output['n'], "scriptPubKey": output['scriptPubKey']['hex'], "redeemScript": p2sh_rscript })
if testnet:
    exodus="mpexoDuSkGGqvqrkrjiFng38QPkJQVFyqv"
else:
    exodus="1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P"

validnextoutputs = { exodus : 0.000055 }

if listOptions['transaction_to'] != None and bool(conn.validateaddress(listOptions['transaction_to']).isvalid):
    validnextoutputs[ listOptions['transaction_to'] ] = 0.000055

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

if len(pubkey) < 100:
    HEXSPACE_FIRST='21'
else:
    HEXSPACE_FIRST='41'

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

#output final product as JSON

if '-armory' in sys.argv:
  sys.argv = ['ArmoryQt.py']
  import holyscript
  listOptions['spending_tx_raw'] = conn.getrawtransaction(listOptions['spending_txid'], False)
  listOptions['spending_tx_decoded'] = conn.decoderawtransaction(listOptions['spending_tx_raw'])
  listOptions['decoded_mptx'] = conn.decoderawtransaction(''.join(hex_transaction))
  listOptions['p2sh_addr_pubkey']=(raw_input("Please enter the MULTISIG ADDRESS PUBLIC KEY (scriptPubkey) from the above that will be spent, required:\n(Enter to use: "+str(p2sh_scriptPubkey)+")") or p2sh_scriptPubkey) 
  #listOptions['p2sh_addr_pubkey']=p2sh_scriptPubkey
  listOptions['p2sh_redeemscript']=(raw_input("Please enter the MULTISIG ADDRESS REDEEM SCRIPT from the above , required:\n(Enter to use: "+str(p2sh_rscript)+")") or p2sh_rscript)  
  #listOptions['p2sh_redeemscript']=p2sh_rscript 
    #= conn.validateaddress(listOptions['transaction_from']).hex

  rawhex = holyscript.holySignor(listOptions, ''.join(hex_transaction), testnet) 

  print ''
  print 'This is your ARMORY hex: '
  print rawhex
  print ''

if '-ui' in sys.argv:
  #dump unsigned
  print ''
  print 'This is your hex: '
  print ''.join(hex_transaction)
  print ''
  sign_it=raw_input('Would you like to sign it now? [yes OR no]')
  if sign_it == 'yes':
     import P2SH_signer
     #P2SH_signer.run_P2SH_sign()
  else: exit()
else:
  print ''.join(hex_transaction)

