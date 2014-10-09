import sys, pprint, textwrap
sys.path.append('/opt/armory-git')
from armoryengine.Transaction import *
from armoryengine.ArmoryUtils import *

# holy offline armory generator v.01
# by fazz k
tnet = 0

def holyDecodor(signed, tnet_):
    global tnet
    tnet = 'fabfb5da' if tnet_ else 'f9beb4d9'

    raw_tx_bin = UnsignedTransaction().unserializeAscii(signed, skipMagicCheck=False).getSignedPyTx(False,False).serialize();
    raw_tx_hex = binary_to_hex(raw_tx_bin)
    return raw_tx_hex

def getMSig(s):
    p2sh_red = getMultisigScriptInfo(hex_to_binary(s)) 

    dats = []
    for each in p2sh_red[2:]:
      dats.append(map( lambda o: binary_to_hex(o), each) )

    dats.insert(0,p2sh_red[1])
    dats.insert(0,p2sh_red[0])
    return dats

def holySignor(opt, scr, tnet_):
    global tnet
    tnet = 'f9beb4d9' if tnet_ else 'f9beb4d9'

    pkdat = getMSig(opt['p2sh_redeemscript']) 
    
    json_nosig = genJSON(opt, pkdat, scr )
 
    return UnsignedTransaction().fromJSONMap(json_nosig, False).serializeAscii()
    

def genJSON( opt , keys, rawtx):
    import decimal 
    #print ''
    #print ''
    #print opt

    #print pprint.pprint(opt['decoded_mptx']['vout'])
    #print pprint.pprint(opt['spending_tx_decoded']['vout'])

    i_vout = -1
    for each in opt['spending_tx_decoded']['vout']:
      print each['scriptPubKey']['hex'] , opt['p2sh_addr_pubkey']
      if each['scriptPubKey']['hex'] == opt['p2sh_addr_pubkey']:
        i_vout = each['n']

    #print '\n ', i_vout, tnet



    i_k = []
    for k in keys[-1]:
      i_k.append( { 'dersighex': '', 'pubkeyhex': k, 'wltlochex': '' } )
    
    o_k = []
    for o in opt['decoded_mptx']['vout']:
      o_k.append( {    'authdata': '',
                       'authmethod': 'NONE',
                       'contribid': '',
                       'contriblabel': '',
                       'magicbytes': tnet,
                       'p2shscript': '',
                       'txoutscript': o['scriptPubKey']['hex'],
                       'txoutvalue': int( o['value'] * decimal.Decimal(1e8) ),
                       'version': 1,
                       'wltlocator': ''}) 

    json_nosig = {
    'id': '',
    'locktimeint': 0, 
    'magicbytes': tnet,
    'version': 1,
    'inputs': [   {   'contribid': '',
                      'contriblabel': '',
                      'keys': i_k,
                      'magicbytes': tnet,
                      'numkeys': keys[0],
                      'p2shscript': opt['p2sh_redeemscript'],
                      'sequence': 4294967295,
                      'supporttx': opt['spending_tx_raw'],
                      'supporttxoutindex': i_vout,
                      'version': 1}],

    'outputs': o_k
    }

    return json_nosig
