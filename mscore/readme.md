How to

text files
```
output2.txt - this is the raw log output of mastercore binary
addrs.txt - this is the output of mscrpc RPC call
omni.txt - this is the verification API for Omni
diffs.txt - these are the diffs for consensus
```

commands
```
mastercore > output2.txt
curl https://test.omniwallet.org/v1/mastercoin_verify/addresses\?currency_id\=1 > omni.txt
python2 filterAddrs.py > parsed-addrs.txt
python2 compareOmniCore.py > diffs.txt
```

other good commands to know:

```
grep update_tally /tmp/mastercore.log.michael | cut -d',' -f1-3
grep update_tally /tmp/mastercore.log.michael | cut -d',' -f1-3 > /tmp/cutlog-michael
grep update_tally /tmp/mastercore.log.bart | cut -d',' -f1-3 > /tmp/cutlog-bart
diff /tmp/cutlog-bart /tmp/cutlog-michael
grep update_tally /tmp/mastercore.log.bart | cut -d',' -f1-3
diff /tmp/cutlog-bart.2 /tmp/cutlog-bart
grep update_tally /tmp/mastercore.log.michael.2 | cut -d',' -f1-3 > /tmp/cutlog-michael.2
grep update_tally /tmp/mastercore.log.bart.2 | cut -d',' -f1-3 > /tmp/cutlog-bart.2
diff /tmp/cutlog-bart.2 /tmp/cutlog-michael.2
```
