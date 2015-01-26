
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

def run_P2SH_sign():
  if len(sys.argv) < 2: 
      exit()

  force=False

  if sys.argv[1] == '-ui':
    import CLI_prompter_P2SH_signer
    listOptions = CLI_prompter_P2SH_signer.callCLI()
  else:
    listOptions = { 
            'unsignedhex': sys.argv[1], 
            'spending_input': sys.argv[2],
            "spending_input_vout": int(sys.argv[3]),
            "p2sh_addr_pubkey": sys.argv[4],     #scriptpubkey
            "p2sh_redeemscript": sys.argv[5],         #p2sh redeemscript
            "privkey": sys.argv[6],                   #privkey to sign with
            "testnet": bool(int(sys.argv[7])) #0 or 1
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
    if sys.argv[8] == 'local':
      conn = bitcoinrpc.connect_to_local()
    elif sys.argv[8] == 'remote':
      conndetails=open(sys.argv[9]).readline().split(':')
      #print conndetails, int(conndetails[4])
      #sort out whether using local or remote API
      conn = bitcoinrpc.connect_to_remote(conndetails[0],conndetails[1],host=conndetails[2],port=int(conndetails[3]),use_https=int(conndetails[4]))
    else:
      print 'connection did not establish: FAIL'
      exit()

  #decode unsigned hex to get input spend (only take 1 at a time i guess)
  #get raw on input, as well as vout
  #using input find p2sh output and get redeemscript
  #redeemscript probably needs to be provided
  #privkey too

  partial_signed_raw_tx = conn.signrawtransaction(listOptions['unsignedhex'], [ { 'txid': listOptions['spending_input'], 'vout': listOptions['spending_input_vout'], 'scriptPubKey': listOptions['p2sh_addr_pubkey'], 'redeemScript': listOptions['p2sh_redeemscript'] } ], [ listOptions['privkey'] ] )

  hex_transaction = partial_signed_raw_tx['hex']
  #verify that transaction is valid
  assert type(conn.decoderawtransaction(''.join(hex_transaction).lower())) == type({})

  #dump unsigned
  if sys.argv[1] == '-ui':
    #dump unsigned
    print ''
    if partial_signed_raw_tx['complete'] == False: print "WARNING: YOUR TRANSACTION IS NOT YET COMPLETELY SIGNED, MAKE SURE YOU SIGN IT WITH ALL REQUIRED ADDRESSES BEFORE TRANSMITTING."
    if partial_signed_raw_tx['complete'] == True: print "SUCCESS: YOUR TRANSACTION IS COMPLETELY SIGNED, GOOD WORK BUDDY."
    print 'This is your hex, buddy: '
    print ''.join(hex_transaction)
    print ''
    if partial_signed_raw_tx['complete'] == False:
      sign_it=raw_input('Would you like to sign it again? [yes OR no]')
      if sign_it == 'yes':
         run_P2SH_sign()
      else: exit()
  else:
    print ''.join(hex_transaction)

run_P2SH_sign()
