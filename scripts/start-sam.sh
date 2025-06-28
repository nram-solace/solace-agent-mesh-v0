#!/bin/bash
SAMHOME=$PWD
SAMBIN=/home/nram/solace/sam/0.2.4/samenv/bin/solace-agent-mesh
LOGFILE=./logs/sam.log
cd $SAMHOME

pid=`pgrep -f ""$SAMBIN""`
if [ "$pid" != "" ]
then
  echo "SAM already started, pid $pid"
  exit 1
fi

nohup $SAMBIN run > $LOGFILE 2>&1 &
sleep 3
pid=`pgrep -f ""$SAMBIN""`
if [ "$pid" == "" ]
then
  echo "SAM not started"
else
  echo "SAM started with PID $pid"
fi
