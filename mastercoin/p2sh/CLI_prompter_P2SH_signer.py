
def callCLI():

  o = { }
  print ""
  print "Welcome to the Mastercoin Smart Property (tm) Raw Transaction Generator!"
  print "You will be asked a few questions, please answer truthfully or else."

  o['testnet']=process_bool( raw_input("Is this intended for Testnet? , required: [0=No, 1=Yes]") )
  o['conndetails']=process_daemon(raw_input("Is the BITCOIN DAEMON running on this machine? , required: [0=No, 1=Yes]"))

  o['privkey']=0 #Only 0 supported
  
  o['unsignedhex']=process_hexstr(raw_input("Please enter the HEX STRING that contains a MULTISIG INPUT, required: [no spaces or extra characters please]"))
  o['spending_input']=process_txid(raw_input("Please enter the TRANSACTION ID that the unsignedhex is attempting to spend, required (only 1 allowed): "))
  o['spending_input_vout']=process_int(raw_input("Please enter the TRANSACTION OUTPUT from the above that will be spent, required: "))
  
  o['p2sh_addr_pubkey']=process_hexstr(raw_input("Please enter the MULTISIG ADDRESS PUBLIC KEY (scriptPubkey) from the above that will be spent, required: ")) 
  o['p2sh_redeemscript']=process_hexstr(raw_input("Please enter the MULTISIG ADDRESS REDEEM SCRIPT from the above , required: "))  

  o['privkey']=process_hexstr(raw_input("Please enter the PRIVATE KEY of one of the addresses in the MULTISIG SCRIPT from the above , required: "))  

  print o
  return o

def input_err(input_,type_):
    print("ERROR: Invalid input, you gave \'" + str(input_) + "\' but we needed a " + type_)
    print("quitting...")
    exit()

def process_daemon(d):
   input_ = d
   type_ = 'boolean integer, 0 or 1'
   try: d = int(d)
   except: input_err(input_, type_)

   rc = []
   if d == 0:
      d = 'remote'
      f=process_string( raw_input("Please enter a absolute filename to a file containing connection details in this format: 'rpcusername:rpcpassword:rpchostname:rpcport:rpcssl', required: [default='', max=255 characters]") )
      rc = [d,f]
   else:
      d='local'
      rc = [d,'']
   return rc

def process_bool(b):
   input_ = b
   type_ = 'boolean integer, 0 or 1'
   try: b = int(b)
   except: input_err(input_, type_)
   return b

def process_int(i):
   input_ = i
   type_ = 'integer, 0 through 9'
   try: i = int(i)
   except: input_err(input_, type_)
   return i

def process_address(a):
   input_ = a
   type_ = 'bitcoin address'
   if len(a) < 32: input_err(input_, type_)
   return a

def process_redeemer(r):
   input_ = r
   type_ = 'bitcoin address'
   
   ret = []
   if r == '': 
    r='04ad90e5b6bc86b3ec7fac2c5fbda7423fc8ef0d58df594c773fa05e2c281b2bfe877677c668bd13603944e34f4818ee03cadd81a88542b8b4d5431264180e2c28'
    ret=['pubkey',r]
   elif len(r) > 30 and len(r) < 36:
    ret=['address',r]
   else:
    ret=['pubkey', r]

   return ret

def process_txid(tx):
   input_ = tx
   type_ = '32-byte bitcoin transaction hash'
   if len(tx) != 64: input_err(input_, type_)
   return tx

def process_string(s):
   return s[:255]

def process_hexstr(s):
   return s
