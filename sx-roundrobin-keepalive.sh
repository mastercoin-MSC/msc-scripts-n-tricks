#Declare necessary vars
SX_CORE=''    #ex. /usr/lib/local/sx-core
WWW_DIR=''    #ex. /tmp
TEMP_HEIGHT=$WWW_DIR/last_height.tmp
PERSIST_HEIGHT=$WWW_DIR/block_height.tmp
STAT_FILE=$WWW_DIR/sx_conn.json

#Declare valid servers
valid[0]='"tcp://obelisk.bysh.me:9091"'
valid[1]='"tcp://obelisk.unsystem.net:9091"'
valid[2]='"tcp://obelisk.unsystem.net:8081"'
valid[3]='"tcp://ottrbutt.com:9091"'

#Init vars and files
ACTIVEINDEX=4

touch $PERSIST_HEIGHT

#Start
while true
do
  echo "$(date) Connecting to: $(cat ~/.sx.cfg)"
  eval "$SX_CORE/sx-fetch-last-height > $TEMP_HEIGHT 2> /dev/null &"
  SXPID=$!
  sleep 8
  #Create test condition if return is success 
  SX_TEST=$(cat $TEMP_HEIGHT)
  if [[ -n $SX_TEST ]]
  then
    #Update block height
    echo $SX_TEST > $PERSIST_HEIGHT
  fi
  #Get last height
  SX_BLOCK=$(cat $PERSIST_HEIGHT)

  #DEBUG
  #echo $(ps -fu user | grep sx-fetch)
  #echo $(kill -0 $SXPID) killpid $? exit_code $SX_TEST test $SXPID pis is $SX_BLOCK block

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

      echo "{ \"status\": \"DOWN\", \"last_known_height\": \""$SX_BLOCK"\" , \"heartbeat_timestamp\": \""$(date)"\" }" > $STAT_FILE
      ACTIVEINDEX=$(($ACTIVEINDEX+1))
    else 
    ACTIVEINDEX=0
    fi
  else
    echo "SX connection established."
    echo "{ \"status\": \"UP\", \"last_known_height\": \""$SX_BLOCK"\" , \"heartbeat_timestamp\": \""$(date)"\" }" > $STAT_FILE
  fi
done

