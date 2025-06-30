#!/bin/bash
#SAMHOME=$PWD
#SAMBIN=/usr/local/bin/solace-agent-mesh
SAMBIN=$(which solace-agent-mesh)
SAMBIN="/home/azureuser/sam/0.2.4/ccgoldminer-v3.1/venv/bin/solace-agent-mesh"
SAMBIN="solace-agent-mesh"
if [ -z ""$SAMBIN"" ]; then
	echo sam is not in path
	echo use source venv/bin/activate first.
	exit
fi


pid=`pgrep -f ""$SAMBIN""`

if [ "$pid" == "" ]
then
  echo "SAM not running."
else
	echo "$(date): SAM running with PID $pid. Stopping..."
  kill $pid
fi

