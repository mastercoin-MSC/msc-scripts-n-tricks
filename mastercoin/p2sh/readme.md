this script folder allows one to do p2sh transactions

run the Ui like so:

```
To generate a property & generate armory outputs:

python2 generateMSP_P2SH.py -ui -armory

OR

To do a grant & generate armory outputs:
python2 generateGR_RV_P2SH.py -ui -armory
```
either of these will start the flow

once you have this ArmoryAscii text blob, go into Armory and sign it

once you have done this, save the text in a file and run 

```

python2 runArmoryDecoder.py 

```
  
it will ask you where the file is and if you wish to generate a transaction in testnet

after this it will spit your raw hex


