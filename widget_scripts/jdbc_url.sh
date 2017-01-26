#!/bin/ksh

dsName=$1
dsUrl=$2
j2cAuthAlias=$3
WAS_PATH=/usr/local/opt/was/was70

$WAS_PATH/bin/wsadmin.sh -lang jython -f webServer.py "$dsName" "$dsUrl" "$j2cAuthAlias"