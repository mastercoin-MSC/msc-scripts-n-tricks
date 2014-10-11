import sys


if len(sys.argv) > 1:
  rawtx = ''.join(open(sys.argv[1]).readlines())

if len(sys.argv) > 2:
  testnet= False if int(sys.argv[2]) == 0 else True

if len(sys.argv) == 1:
  rawtx=''.join(open(raw_input("Enter the filename of the ArmoryAscii-encoded transaction, required: ") ).readlines())
  testnet= False if int(raw_input("Is this intended for Testnet? , required: [0=No, 1=Yes]")) == 0 else True


if testnet:
  sys.argv = ['ArmoryQt.py', '--testnet']
else:
  sys.argv = ['ArmoryQt.py']
import holyscript
u_hex= holyscript.holyDecodor(rawtx, testnet) 
print 'your hex is: \n'
print u_hex
print '\nthx' 
exit()
