#!/bin/bash
#SAMHOME=$PWD
#SAMBIN=/usr/local/bin/solace-agent-mesh
SAMBIN=$(which solace-agent-mesh)


pid=`pgrep -f ""$SAMBIN""`

if [ "$pid" == "" ]
then
  echo "SAM not running."
else
	echo "$(date): SAM running with PID $pid. Stopping..."
  kill $pid
fi

