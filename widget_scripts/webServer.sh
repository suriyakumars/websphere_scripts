#!/bin/ksh

opType=$1
ihsNode=$2
ihsServer=$3
WAS_PATH=/usr/local/opt/was/was70

$WAS_PATH/bin/wsadmin.sh -lang jython -f webServer.py "$opType" "$ihsNode" "$ihsServer"