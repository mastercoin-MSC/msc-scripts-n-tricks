# Counterparty decoder
# GPLv3, Faiz K.

import sys,re, binascii, struct, bitcoinrpc, pybitcointools

print '\n'

if len(sys.argv) < 3 : print "\nUSAGE: \ncat python2 counterparty_decoder.py source tx_hash testnet[default=0] service[default=bitcoind]\n", exit()

listOptions = { 'source': sys.argv[1], 'transaction': sys.argv[2], 'testnet': bool(int(sys.argv[3]))  }

testnet=False
magicbyte=0
if listOptions['testnet']:
  testnet=True
  magicbyte=111

#sort out whether using local or remote API
conn = bitcoinrpc.connect_to_local()

transaction = conn.getrawtransaction(listOptions['transaction'])
inputs = transaction.vin
#senders address
source = listOptions['source']
compressed = listOptions['source']

possible_burn=False

#get all data
data_output = []
for output in transaction.vout:
    for address in output['scriptPubKey']['addresses']:
      if len(re.findall('counterparty', address, re.I)) != 0:
        possible_burn=True
    if output['scriptPubKey']['type'] == 'multisig' or output['scriptPubKey']['type'] == 'nulldata':
        data_output.append(output) #grab msigs

#extract compressed keys
scriptkeys = []
for output in data_output:
    split_script = output['scriptPubKey']['asm'].split(' ')
    for val in split_script:
        if len(val) == 66 or len(val) == 46:
            scriptkeys.append(val)

#filter keys that are ref
nonrefkeys = []
for datahex in scriptkeys:
    if len(datahex) == 66:
      if pybitcointools.pubtoaddr(datahex, magicbyte) != source and pybitcointools.pubtoaddr(datahex, magicbyte) != compressed:
          nonrefkeys.append(datahex)
    else:
      nonrefkeys.append(datahex)

packets = nonrefkeys

import Crypto.Cipher.ARC4
key = Crypto.Cipher.ARC4.new(binascii.unhexlify(inputs[0]['txid']))

long_packet = []
for packet in packets:
    packet = binascii.hexlify(key.decrypt(binascii.unhexlify(packet)))
    print 'Encoded packet Found : ' + packet

    long_packet += binascii.unhexlify(packet)[1:]

print '\n'

if len(long_packet) == 0 and possible_burn:
   print 'Possible XCP burn, no data to decode...', exit()

#strip leading and ending nulldata
b = 0
for i in range(0,len(long_packet)):
  byte = long_packet[i]
  if byte == '\x00':
    long_packet = long_packet[i:]
    break

#debug print [long_packet]

def decode_(fmt, packet, size, s, p=0, str_=False):
  #debug print packet[:size]

  v = struct.unpack(fmt, ''.join(packet[0:size]) )[0] 
  
  if str_:
    v = binascii.hexlify(v).decode('utf-8')
  
  print s + ': ' + str(v)

  if p == 1: 
    return long_packet[size:], v
  else:
    return long_packet[size:]

long_packet, msg_id = decode_('>I', long_packet, 4, 'Message type', 1)

if msg_id == 0: 

    print 'Send: '
    long_packet = decode_('>Q', long_packet, 8, 'Asset Id')
    long_packet = decode_('>Q', long_packet, 8, 'Quantity')

if msg_id == 20:  #only decodes newest version
    
    print 'Issuance: '
    long_packet = decode_('>Q', long_packet, 8, 'Asset Id')
    long_packet = decode_('>Q', long_packet, 8, 'Quantity')
    long_packet = decode_('>?', long_packet, 1, 'Divisible?')
    long_packet = decode_('>?', long_packet, 1, 'Calllable?')
    long_packet = decode_('>I', long_packet, 4, 'Call date')
    long_packet = decode_('>f', long_packet, 4, 'Call price')
    description = ''.join(long_packet).decode('utf-8')

    print 'Description: ' + str( description)

if msg_id == 80:

    print 'RPS: '
    long_packet = decode_('>H', long_packet, 2, 'Possible moves')
    long_packet = decode_('>Q', long_packet, 8, 'Wager')
    long_packet = decode_('>32s', long_packet, 32, 'Move random hash', 0, True)
    long_packet = decode_('>I', long_packet, 4, 'Expiration')

if msg_id == 10:

    print 'Order: '
    long_packet = decode_('>Q', long_packet, 8, 'Able-to-give asset id')
    long_packet = decode_('>Q', long_packet, 8, 'Able-to-give quanitity')
    long_packet = decode_('>Q', long_packet, 8, 'Will-get asset id')
    long_packet = decode_('>Q', long_packet, 8, 'Will-get quantity')
    long_packet = decode_('>H', long_packet, 2, 'Expiration')
    long_packet = decode_('>Q', long_packet, 8, 'Fee required')

if msg_id == 30:

    print 'Broadcast: '
    long_packet = decode_('>I', long_packet, 4, 'Timestamp')
    long_packet = decode_('>d', long_packet, 8, 'Value')
    long_packet = decode_('>I', long_packet, 4, 'Fee fraction')
    text = ''.join(long_packet).decode('utf-8')

    print 'Text: ' + str(text)

if msg_id == 40:
    
    bet_type_str = ['BullCFD', 'BearCFD', 'Equal', 'NotEqual']

    print 'Bet: '
    long_packet, bet_type = decode_('>H', long_packet, 2, 'Bet type', 1)
    print 'Bet type: ', bet_type_str[ bet_type ]
    long_packet = decode_('>I', long_packet, 4, 'Deadline')
    long_packet = decode_('>Q', long_packet, 8, 'Wager amount')
    long_packet = decode_('>Q', long_packet, 8, 'Counterwager amount')
    long_packet = decode_('>d', long_packet, 8, 'Target value')
    long_packet = decode_('>I', long_packet, 4, 'Leverage')
    long_packet = decode_('>I', long_packet, 4, 'Expiration')

if msg_id == 50:

    print 'Dividend: '
    long_packet = decode_('>Q', long_packet, 8, 'Quantity per unit')
    long_packet = decode_('>Q', long_packet, 8, 'Asset id')
    long_packet = decode_('>Q', long_packet, 8, 'Dividend asset id')

if msg_id == 70:

    print 'Cancel: '
    long_packet = decode_('>32s', long_packet, 32, 'TxId', 0, True)

if msg_id == 21:

    print 'RPS Resolve: '
    long_packet = decode_('>H', long_packet, 2, 'Move')
    long_packet = decode_('>16s', long_packet, 16, 'Random', 0, True)
    long_packet = decode_('>32s', long_packet, 32, 'TxId0', 0, True)
    long_packet = decode_('>32s', long_packet, 32, 'TxId1', 0, True)

if msg_id == 21:

    print 'Callback: '
    long_packet = decode_('>d', long_packet, 8, 'Fraction')
    long_packet = decode_('>Q', long_packet, 8, 'Asset id')

if msg_id == 11:

    print 'BTCPay: '
    long_packet = decode_('>32s', long_packet, 32, 'TxId0', 0, True)
    long_packet = decode_('>32s', long_packet, 32, 'TxId1', 0, True)

if msg_id == 100:

    print 'Publish: '
    print 'Data: ' , binascii.hexlify(''.join(long_packet))
    print 'Data-Interpreted: ', ''.join(long_packet)


print '\n'
