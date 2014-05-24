URL="https://test.omniwallet.org"
REPO_URL="https://raw.githubusercontent.com/mastercoin-MSC/omniwallet/master"
while :
do
  echo Updated: "$(date)" > ~/uptime

  SITEDATA=$(curl $URL -s)
  echo $SITEDATA | grep "thanks to joseph" -q
  SITECODE=$?
  if [[ $SITECODE -eq 0 ]]; then
    echo "Site loaded successfully (URL: $URL)" >> ~/uptime
  else
    echo "Site did not load successfully (URL: $URL)" >> ~/uptime
  fi

  URL_VERIFY="$URL/v1/mastercoin_verify/addresses?currency_id=1"
  APIDATA=$(curl $URL_VERIFY -s )
  echo $APIDATA | grep 1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P -q
  SITECODE=$?
  if [[ $SITECODE -eq 0 ]]; then
    echo "API loaded successfully (URL: $URL)" >> ~/uptime
  else
    echo "API did not load successfully (URL: $URL)" >> ~/uptime
  fi

  REVISION=$(curl -s $URL/v1/system/revision.json)
  LASTBLOCK=$(echo $REVISION | jq '.last_block')
  SXLASTBLOCK=$(sx history -j 1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P | jq '[.[] | .output_height] - ["Pending"] | max') 
  if [[ $SXLASTBLOCK -eq $LASTBLOCK ]]; then
    echo "Omniwallet parser is up to date at $SXLASTBLOCK" >> ~/uptime
  else
    echo "Omniwallet parser is not up to date at $LASTBLOCK, most recent is $SXLASTBLOCK" >> ~/uptime
  fi

  SITEDATA=$(curl http://btc.blockr.io/api/v1/coin/info -s)
  LASTBLOCK=$(echo $SITEDATA | jq '.data | .last_block | .nb')

  SXBLOCK=$( sx fetch-last-height)
  if [[ $SXBLOCK -eq $LASTBLOCK ]]; then
    echo "Obelisk server is up to date at $SXBLOCK" >> ~/uptime
  else
    echo "Obelisk server is not up to date at $LASTBLOCK, most recent is $SXBLOCK" >> ~/uptime
  fi
  
  #SHA
  FILE="AssetTypesController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5

  FILE="CreateWalletController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5
  
  FILE="LoginController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5

  FILE="WalletAddressesController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5

  FILE="WalletBuyAssetsController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5

  FILE="WalletController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5
  
  FILE="WalletSellAssetsController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5
  
  FILE="WalletSendAssetsController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  sleep 5
  
  FILE="WalletTradeFormController.js"
  JAVASCRIPT_GITHUB=$(curl -s $REPO_URL/www/js/$FILE)
  JAVASCRIPT=$(curl -s $URL/js/$FILE)
  SHA_GITHUB=$(echo -n "$JAVASCRIPT_GITHUB" | sha256sum )
  SHA=$(echo -n "$JAVASCRIPT" | sha256sum )
  if [[ $SHA = $SHA_GITHUB ]]; then
    echo "$FILE is OK (Site/Github): $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  else
    echo "$FILE is NOT OK (Site/Github) $(echo -n $SHA | cut -c -10) | $(echo -n $SHA_GITHUB | cut -c -10)" >> ~/uptime
  fi
  
  sleep 5
  
  cp ~/uptime ~/uptime.html
  echo "Done, sleeping..."
  sleep 60
done
