### msc scripts n tricks

Dependencies:
Several of these scripts reference additional python libraries. 
bitcoin-python "http://laanwj.github.com/bitcoin-python/doc/"
pybitcointools "http://github.com/vbuterin/pybitcointools"
We recommend the installation of these via pip
```
pip install bitcoin-python pybitcointools
```

these are some scripts where it might be useful for developers to hack around with the protocol
or just some hacks that might be useful

```
deobfus.py deobfuscates MSC packets for debugging
generateTX* generates the appropriate transaction from the cmd line given input from JSON
getbalance gets balances of MSC addresses
geConsensus calculates consesnsus
redeemMultisig redeems dust or multisig (1 of n) outs automatically (if you're a msc dev, very useful)
```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
