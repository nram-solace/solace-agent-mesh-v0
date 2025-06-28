#!/bin/bash
SAMHOME=$PWD
SAMBIN=$(which solace-agent-mesh)
[ -d ./logs ] || mkdir logs
LOGFILE=./logs/sam.log
cd $SAMHOME

pid=`pgrep -f ""$SAMBIN""`
if [ "$pid" != "" ]
then
  echo "SAM already started, pid $pid"
  exit 1
fi

nohup $SAMBIN run -b > $LOGFILE 2>&1 &
sleep 3
pid=`pgrep -f ""$SAMBIN""`
if [ "$pid" == "" ]
then
  echo "SAM not started"
else
	echo "$(date):  SAM started with PID $pid"
fi
