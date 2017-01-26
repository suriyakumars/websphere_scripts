#!/bin/ksh

opType=$1
cluster_names=$2

WAS_PATH=/usr/local/opt/was/was70

$WAS_PATH/bin/wsadmin.sh -lang jython -f cluster.py "$opType" "$cluster_names"