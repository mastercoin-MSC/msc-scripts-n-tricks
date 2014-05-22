while :
do
  echo Updated: "$(date)" > ~/uptime

  URL="https://test.omniwallet.org"
  SITEDATA=$(curl $URL -s)
  echo $SITEDATA | grep "thanks to joseph" -q
  SITECODE=$?
  if [[ $SITECODE -eq 0 ]]; then
    echo "Site loaded successfully (URL: $URL)" >> ~/uptime
  else
    echo "Site did not load successfully (URL: $URL)" >> ~/uptime
  fi

  URL="https://test.omniwallet.org/v1/mastercoin_verify/addresses?currency_id=1"
  APIDATA=$(curl $URL -s )
  echo $APIDATA | grep 1EXoDusjGwvnjZUyKkxZ4UHEf77z6A5S4P -q
  SITECODE=$?
  if [[ $SITECODE -eq 0 ]]; then
    echo "API loaded successfully (URL: $URL)" >> ~/uptime
  else
    echo "API did not load successfully (URL: $URL)" >> ~/uptime
  fi

  REVISION=$(curl -s https://test.omniwallet.org/v1/system/revision.json)
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

  echo "Done, sleeping..."
  sleep 60
done

