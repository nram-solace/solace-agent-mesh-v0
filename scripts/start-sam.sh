#!/bin/bash
SAMHOME=$PWD
SAMBIN=$(which solace-agent-mesh)
SAMHOME="/home/azureuser/sam/0.2.4/ccgoldminer-v3.1/"
source venv/bin/activate
SAMBIN="$SAMHOME/venv/bin/solace-agent-mesh"
if [ -z ""$SAMBIN"" ]; then
	echo sam is not in path
	echo use source venv/bin/activate first.
	exit
fi
#if [ -x ""$SAMBIN"" ]; then
#	echo sam is not executable
#	exit
#fi
#echo $0: SAM binary is $SAMBIN

echo Cleanup old logs
[ -d ./logs ] || mkdir logs
rm logs/* *.log trace*txt 2> /dev/null
LOGFILE=./logs/sam.log
cd $SAMHOME

echo Check if SAM is running already
pid=`pgrep -f ""$SAMBIN""`
if [ "$pid" != "" ]
then
  echo "SAM already started, pid $pid"
  exit 1
fi

# Start MySQL
echo "Starting MySQL"
sudo systemctl start mysql
sleep 10
sudo systemctl status mysql

echo "Starting Solace"
sudo docker start solace
sleep 10 #  WARNING! This is not enough time
sudo docker ps | egrep "CONTAINER|solace"
sudo docker inspect -f '{{.State.Running}}' solace

echo Start SAM 
echo $SAMBIN run -b ...
nohup $SAMBIN run -b > $LOGFILE 2>&1 &
sleep 3
pid=`pgrep -f ""$SAMBIN""`
if [ "$pid" == "" ]
then
  echo "SAM not started"
else
	echo "$(date):  SAM started with PID $pid"
fi
echo Logfile is $LOGFILE
