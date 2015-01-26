This is supposed to work like 'getrawtransaction' does for bitcoind, sort of. 

You should have a working Bitcoin node running in the background before running this program.

Testnet or Mainnet is fine.

```
USAGE: python counterparty_decoder.py (sender address) (tx_hash)
```

Example output:

*Testnet
```
python2 counterparty_decoder.py mfaiZGBkY4mBqt3PHPD2qWgbaafGa7vR64 6d5789458184d1064b6637cd2b6887f08c022096ccd7f0c99dd736c46e1822c3


Encoded packet Found : 20434e5452505254590000000a000000000000fc16000000000000000100000000
Encoded packet Found : 1600000001000000003b9aca0000ff000000000000000000000000000000000000


Message type: 10
Order: 
Able-to-give asset id: 64534
Able-to-give quanitity: 1
Will-get asset id: 1
Will-get quantity: 1000000000
Expiration: 255
Fee required: 0
```
*Mainnet
```
python2 counterparty_decoder.py  13s8t8Dp7aqqxrEu1mAcaHAnyT9y7GkeAp f02c51bc6b2b2ab9990a6bd7da7e9164c8fe182987118a400aa3bce265f02437


Encoded packet Found : 20434e5452505254590000001e543e89d2bff00000000000000007a12014626574
Encoded packet Found : 117863702e636f6d2f666565642f32363837000000000000000000000000000000


Message type: 30
Broadcast: 
Timestamp: 1413384658
Value: -1.0
Fee fraction: 500000
Text: betxcp.com/feed/2687

```
Limited support for burns (tx60) and older/deprecated versions of various transaction classes, assume that you will be parsing transactions made from a relatively new version of counterpartyd.

Suggestions and improvements most welcome, thanks.

