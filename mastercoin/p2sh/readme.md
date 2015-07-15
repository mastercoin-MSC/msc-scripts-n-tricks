YOU NEED TO HAVE DONE THE FOLLOWING:

* Added the p2sh address sending the transaction to the wallet using 'addmultisig'
* If you want to run the armory utils install the armory python libraries

Modified from https://bitcoinarmory.com/building-from-source/
```
sudo apt-get install git-core build-essential pyqt4-dev-tools swig libqtcore4 libqt4-dev python-qt4 python-dev python-twisted python-psutil
git clone git://github.com/etotheipi/BitcoinArmory.git
cd BitcoinArmory
make
sudo make install
```


this script folder allows one to do p2sh transactions

run the Ui like so:

```
To generate a property & generate armory outputs:

python2 generateMSP_P2SH.py -ui -armory

OR

To do a grant & generate armory outputs:
python2 generateGR_RV_P2SH.py -ui -armory

OR

To do a simple send & generate armory outputs:
python2 generateSEND+P2SH.py -ui -armory

```
either of these will start the flow

once you have this ArmoryAscii text blob, go into Armory and sign it

once you have done this, save the text in a file and run 

```

python2 runArmoryDecoder.py 

```
  
it will ask you where the file is and if you wish to generate a transaction in testnet

after this it will spit your raw hex


