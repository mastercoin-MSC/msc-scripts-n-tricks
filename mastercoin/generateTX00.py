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

HEXSPACE='41' #change this to 21 if your hex decode is malformed, system dependent value

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

#check for testnet addr
privkey_char1 = listOptions['from_private_key'][0]
if privkey_char1 == 'c' or privkey_char1 == '9':
   testnet=True

if not testnet:
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

unspent_tx = []
for unspent in conn.listunspent():
    if unspent.address == listOptions['transaction_from']:
        unspent_tx.append(unspent)
#get all unspent for our from_address

for unspent in unspent_tx:
   available_balance = unspent.amount + available_balance

#check if minimum BTC balance is met
print available_balance, 0.00006*3
if available_balance < Decimal(0.00006*3) and not force:
    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#generate public key of bitcoin address 
validated = conn.validateaddress(listOptions['transaction_from'])
if 'pubkey' in validated.__dict__: 
    pubkey = validated.pubkey
elif not force:
    print json.dumps({ "status": "NOT OK", "error": "from address is invalid or hasn't been used on the network" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#find spendable input from UTXO
smallest_spendable_input = { "txid": "", "amount": Decimal(0) }
for unspent in unspent_tx:
    if Decimal(unspent.amount) > Decimal(0.0004) and (smallest_spendable_input['amount'] == Decimal(0) or unspent.amount < smallest_spendable_input['amount']):
        smallest_spendable_input = { "txid": unspent.txid, "amount": unspent.amount }

#real stuff happens here:

broadcast_fee = 0.0001  
output_minimum = 0.0006 #dust threshold

fee_total = Decimal(0.0001) + Decimal(0.00006 * 4)
change = smallest_spendable_input['amount'] - fee_total
# calculate change : 
# (total input amount) - (broadcast fee) - (total transaction fee)

print fee_total, smallest_spendable_input['amount']
if (Decimal(change) < Decimal(0) or fee_total > smallest_spendable_input['amount']) and not force:
    print json.dumps({ "status": "NOT OK", "error": "Not enough funds" , "fix": "Set \'force\' flag to proceed without balance checks" })
    exit()

#build multisig data address

from_address = listOptions['transaction_from']
transaction_type = 0   #simple send
sequence_number = 1    #packet number
currency_id = int(listOptions['currency'])        #MSC
amount = int(listOptions['msc_send_amt']*1e8)  #maran's impl used float??

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

if not testnet:
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
prev_tx = conn.getrawtransaction(smallest_spendable_input['txid'])

validnextinputs = []                      #get valid redeemable inputs
for output in prev_tx.vout:
    if output['scriptPubKey']['reqSigs'] == 1 and output['scriptPubKey']['type'] != 'multisig':
        for address in output['scriptPubKey']['addresses']:
            if address == listOptions['transaction_from']:
                validnextinputs.append({ "txid": prev_tx.txid, "vout": output['n']})

validnextoutputs = { "1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P": 0.00006 , listOptions['transaction_to'] : 0.00006 }

if change > Decimal(0.00006): # send anything above dust to yourself
    validnextoutputs[ listOptions['transaction_from'] ] = float(change) 

unsigned_raw_tx = conn.createrawtransaction(validnextinputs, validnextoutputs)

json_tx =  conn.decoderawtransaction(unsigned_raw_tx)

#add multisig output to json object
json_tx['vout'].append({ "scriptPubKey": { "hex": "51" + HEXSPACE + pubkey + "21" + data_pubkey.lower() + "52ae", "asm": "1 " + pubkey + " " + data_pubkey.lower() + " 2 OP_CHECKMULTISIG", "reqSigs": 1, "type": "multisig", "addresses": [ pybitcointools.pubkey_to_address(pubkey), pybitcointools.pubkey_to_address(data_pubkey) ] }, "value": 0.00006*2, "n": len(validnextoutputs)})

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

