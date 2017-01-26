#################### This script can be used to start / stop / get status of one or more webserver(s) ###############################
#
# Author: Suriyakumar Subramanian
# Date: 09/02/2010
# USAGE: <WAS_PATH>/wsadmin.sh -f <path/webServer.py> <start|stop|status> <IHS_Node1,IHS_Node2,...> <IHS_Server1,IHS_Server2,...>
# USAGE Example: 
####################################################################################################

import sys
cellName = AdminControl.getCell()
dmgrNode = AdminControl.getNode()

opType = sys.argv[0]
ihsNode = sys.argv[1]
ihsServer = sys.argv[2]

def checkStatus (serverSet):
	status = doServerAction("ping", serverSet)
	return status

def stopServer (serverSet):
	status = doServerAction("stop", serverSet)
	return status

def startServer (serverSet):
	status = doServerAction("start", serverSet)
	return status

def doServerAction (action, serverSet):
	AdminControl.invoke(webServerId, action, serverSet, '[java.lang.String java.lang.String java.lang.String]')

def ihsCheckStatus (ihsNodeList, ihsServerList):
	i = 0
	for eachNode in ihsNodeList:
		ihsNode = eachNode
		ihsServer = ihsServerList[i]
		print "Checking status for WebServer : "+ihsServer
		serverSet = "["+cellName+" "+ihsNode+" "+ihsServer+"]"
		returnStatus = checkStatus (serverSet)
		if (returnStatus == "RUNNING"):
			print "Server is in "+returnStatus+" state"
		else:
			print "Server is in "+returnStatus+" state"	
		i = i + 1
		
def ihsStopServers (ihsNodeList, ihsServerList):
	i = 0
	for eachNode in ihsNodeList:
		ihsNode = eachNode
		ihsServer = ihsServerList[i]
		print "Stopping WebServer : "+ihsServer
		serverSet = "["+cellName+" "+ihsNode+" "+ihsServer+"]"
		returnStatus = stopServer(serverSet)
		if (returnStatus == "true"):
			print "Server stopped successfully"
		else:
			print "Server failed to stop"	
		i = i + 1
		
def ihsStartServers (ihsNodeList, ihsServerList):
	i = 0
	for eachNode in ihsNodeList:
		ihsNode = eachNode
		ihsServer = ihsServerList[i]
		print "Starting WebServer : "+ihsServer
		serverSet = "["+cellName+" "+ihsNode+" "+ihsServer+"]"
		returnStatus = startServer(serverSet)
		if (returnStatus == "true"):
			print "Server started successfully"
		else:
			print "Server failed to start"	
		i = i + 1
		
#execution starts here
webServerId = "WebSphere:name=WebServer,process=dmgr,platform=common,node="+dmgrNode+",version=7.0.0.7,type=WebServer,mbeanIdentifier=WebServer,cell="+cellName+",spec=1.0"

ihsNodeList = []
ihsServerList = []

ihsNode=ihsNode.split(",")
for each in ihsNode:
	ihsNodeList.append(each)
	continue

ihsServer=ihsServer.split(",")
for each1 in ihsServer:
	ihsServerList.append(each1)
	continue

if (opType == "status"):
	
	ihsCheckStatus (ihsNodeList, ihsServerList)

elif (opType == "stop"):

	ihsStopServers (ihsNodeList, ihsServerList)
	
elif (opType == "start"):
	
	ihsStartServers (ihsNodeList, ihsServerList)	
	
else:
	print "Please provide a valid Operation Type (status | start | stop)"
	

