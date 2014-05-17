#Declare valid servers
SX_CORE=/usr/local/lib/sx-core
valid[0]='"tcp://obelisk.bysh.me:9091"'
valid[1]='"tcp://obelisk.unsystem.net:9091"'
valid[2]='"tcp://obelisk.unsystem.net:8081"'
valid[3]='"tcp://ottrbutt.com:9091"'
valid[4]='"tcp://54.187.205.158:9091"'
ACTIVEINDEX=4
while true
do
  echo "Attempting connection with $(cat ~/.sx.cfg)..."
  eval "$SX_CORE/sx-fetch-last-height > /dev/null 2>&1 &" 
  SXPID=$!
  sleep 5
  SUCCESS=$($(kill -0 $SXPID > /dev/null 2>&1); echo $?)
  #echo "PID IS $SXPID SUCCESS IS $SUCCESS"
  if [[ $SUCCESS -eq 0 ]]; then
    
    disown $SXPID
    kill -9 $SXPID > /dev/null 2>&1 #kill sx fetch-last-height

    #echo "ACTIVEINDEX IS $ACTIVEINDEX" 
    if [[ $ACTIVEINDEX -lt ${#valid[*]} ]]
    then
    #Kill SX proc for taking too long
      echo "service=${valid[$ACTIVEINDEX]}" > ~/.sx.cfg
      echo "Taking too long, switching server to $(cat ~/.sx.cfg)...\n"
      ACTIVEINDEX=$(($ACTIVEINDEX+1))
    else 
    ACTIVEINDEX=0
    fi
  else
    echo "SX connection established."
    #ACTIVE=$i
  fi
done

New Relic
