import sys
import holyscript
rawtx = ''.join(open(sys.argv[1]).readlines())
testnet= False if int(sys.argv[2]) == 0 else True
u_hex= holyscript.holyDecodor(rawtx, testnet) 
print 'your hex is: \n'
print u_hex
print '\nthx' 
exit()
