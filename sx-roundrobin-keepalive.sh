#Declare valid servers
SX_CORE=/usr/local/lib/sx-core
WWW_DIR=/tmp
valid[0]='"tcp://obelisk.bysh.me:9091"'
valid[1]='"tcp://obelisk.unsystem.net:9091"'
valid[2]='"tcp://obelisk.unsystem.net:8081"'
valid[3]='"tcp://ottrbutt.com:9091"'
valid[4]='"tcp://54.187.205.158:9091"'
ACTIVEINDEX=4
while true
do
  echo "$(date) Connecting to: $(cat ~/.sx.cfg)"
  eval "$SX_CORE/sx-fetch-last-height 2> /dev/null &" > /tmp/last_height.tmp
  SXPID=$!
  sleep 8

  #Create test condition if return is success 
  SX_TEST=$(cat /tmp/last_height.tmp)
  if [[ -n $SX_TEST ]]
  then
    #Update block height
    echo $SX_TEST > /tmp/block_height.tmp
  fi
  #Get last height
  SX_BLOCK=$(cat /tmp/block_height.tmp)
  #Check if sx is still running
  SUCCESS=$($(kill -0 $SXPID > /dev/null 2>&1); echo $?)
  #echo "PID IS $SXPID SUCCESS IS $SUCCESS"
  if [[ $SUCCESS -eq 0 ]]; then
    
    disown $SXPID
    kill -9 $SXPID > /dev/null 2>&1 #kill sx fetch-last-height

    if [[ $ACTIVEINDEX -lt ${#valid[*]} ]] #this is the index of the array above
    then
    #Kill SX proc for taking too long
      echo "service=${valid[$ACTIVEINDEX]}" > ~/.sx.cfg
      echo "$(date) No response, seeking..."

      echo "{ \"status\": \"DOWN\", \"last_known_height\": \""$SX_BLOCK"\" , \"heartbeat_timestamp\": \""$(date)"\" }" > $WWW_DIR/sx_conn.json
      ACTIVEINDEX=$(($ACTIVEINDEX+1))
    else 
    ACTIVEINDEX=0
    fi
  else
    echo "SX connection established."
    echo "{ \"status\": \"UP\", \"last_known_height\": \""$SX_BLOCK"\" , \"heartbeat_timestamp\": \""$(date)"\" }" > $WWW_DIR/sx_conn.json
  fi
done
