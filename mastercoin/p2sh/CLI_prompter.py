
def callCLI(txType):

  o = { 'transaction_type': txType }
  print ""
  print "Welcome to the Mastercoin Smart Property (tm) Raw Transaction Generator!"
  print "You will be asked a few questions, please answer truthfully or else."
  print ""
  print "WARNING: YOU WILL NEED THE FOLLOWING INFORMATION TO COMPLETE THIS TRANSACTION: "
  print "(transaction to spend, multisignature address, redemption address)"

  o['testnet']=process_bool( raw_input("Is this intended for Testnet? , required: [0=No, 1=Yes]") )
  o['conndetails']=process_daemon(raw_input("Is the BITCOIN DAEMON running on this machine? , required: [0=No, 1=Yes]"))

  if txType == 0:
    o['transaction_from']=process_address(raw_input("Please enter the MULTISIG ADDRESS that will be used in securing funds, required: "))
    o['spending_txid']=process_txid(raw_input("Please enter a TRANSACTION ID that has enough Bitcoin to perform the transaction, required: "))
    o['spending_txid_output']=process_decimal(raw_input("Please enter the TRANSACTION AMOUNT of the outpoint being spent, required: "))

    o['property_id']=process_int(raw_input("Please enter the PROPERTY ID of the property you wish to send, required: "))
    o['number_properties']=process_int(raw_input("Please enter the NUMBER OF PROPERTIES that will be sent, required: [satoshi amounts only, please] "))
    o['redeemer_addr']=process_redeemer(raw_input("Please enter the REDEMPTION ADDRESS (if you own the private key) or the public key of an address that will be used to retreive multisignature outputs, optional: [default=1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P]"))
    o['transaction_to']=process_address(raw_input("Please enter an ADDRESS that you wish to send to, required: "), 1)

  if txType == 54:
    o['ecosystem']=process_int(raw_input("Please enter the ECOSYSTEM you wish to generate a property for, required: [1=Main Ecosystem, 2=Test Ecosystem]"))
    o['property_type']=process_int(raw_input("Please enter the PROPERTY TYPE you wish your property to be, required: [1=Indivisible, 2=Divisible]"))
    o['transaction_from']=process_address(raw_input("Please enter the MULTISIG ADDRESS that will be used in securing funds, required: "))
    o['spending_txid']=process_txid(raw_input("Please enter a TRANSACTION ID that has enough Bitcoin to perform the transaction, required: "))
    o['spending_txid_output']=process_decimal(raw_input("Please enter the TRANSACTION AMOUNT of the outpoint being spent, required: "))
    
    o['previous_property_id']=0 #Only 0 supported
    o['property_name']=process_string( raw_input("Please enter a NAME for your property, required: [max=255 characters]") )
    o['property_category']=process_string( raw_input("Please enter a CATEGORY for your property to be in, optional: [default='', max=255 characters]") )
    o['property_subcategory']=process_string( raw_input("Please enter a SUBCATEGORY for your property to be in, optional: [default='', max=255 characters]") )
    o['property_url']=process_string( raw_input("Please enter a URL for your property, optional: [default='', max=255 characters]") )
    o['property_data']=process_string( raw_input("Please enter any additional notes about your property if any, optional: [default='', max=255 characters]") )

    o['redeemer_addr']=process_redeemer(raw_input("Please enter the REDEMPTION ADDRESS (if you own the private key) or the public key of an address that will be used to retreive multisignature outputs, optional: [default=1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P]"))

  if txType == 55: #grant or revoke
    o['transaction_type']=process_int(raw_input("Is this a GRANT or a REVOKE?, required: [55=Grant, 56=Revoke]"))
    o['transaction_from']=process_address(raw_input("Please enter the MULTISIG ADDRESS that will be used in securing funds, required: "))
    o['spending_txid']=process_txid(raw_input("Please enter a TRANSACTION ID that has enough Bitcoin to perform the transaction, required: "))
    o['spending_txid_output']=process_decimal(raw_input("Please enter the TRANSACTION AMOUNT of the outpoint being spent, required: "))

    o['property_id']=process_int(raw_input("Please enter the PROPERTY ID of the property you wish your grant/revoke to be, required: "))
    o['number_properties']=process_int(raw_input("Please enter the NUMBER OF PROPERTIES that will be granted or revoked in the transaction, required: [satoshi amounts only, please] "))
    o['memo']=process_string( raw_input("Please enter any additional notes about your property if any, optional: [default='', max=255 characters]") )
    o['redeemer_addr']=process_redeemer(raw_input("Please enter the REDEMPTION ADDRESS (if you own the private key) or the public key of an address that will be used to retreive multisignature outputs, optional: [default=1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P]"))
    o['transaction_to']=process_address(raw_input("Please enter an ADDRESS that you wish to grant/revoke to, optional: "), 1)
    
  return o

def input_err(input_,type_):
    print("ERROR: Invalid input, you gave \'" + str(input_) + "\' but we needed a " + type_)
    print("quitting...")
    exit()

def process_decimal(dec):
  import decimal
  return decimal.Decimal(dec)

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

def process_address(a, branch=0):
   input_ = a
   type_ = 'bitcoin address'
   if branch == 0:
     if len(a) < 32: input_err(input_, type_)
   if branch == 1:
     if a == '': a = None 
     a = input_err(input_, type_) if (a != None) and (len(a) < 32) else a
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
